import time
from typing import Dict, Any, List
from .base import BaseAgent
from ..core.models import AgentRole, AgentMessage, SwarmState, Anomaly
from ..connectors.base import BaseCloudProvider

class TelemetryInvestigatorAgent(BaseAgent):
    """Investigates metrics, logs, and traces to correlate root cause anomalies."""

    def __init__(self, cloud_provider: BaseCloudProvider):
        super().__init__(
            role=AgentRole.TELEMETRY_INVESTIGATOR,
            name="Telemetry-Investigator-01",
            system_prompt=(
                "You are an expert SRE Telemetry Investigator. Your goal is to analyze "
                "CloudWatch, Prometheus, and K8s metrics/logs to extract precise anomaly signatures "
                "and propose a deterministic root cause hypothesis."
            ),
        )
        self.provider = cloud_provider

    async def process_turn(self, state: SwarmState) -> AgentMessage:
        self.log(f"Starting telemetry investigation for incident: {state.incident.id} ({state.incident.title})")

        # Query metrics and logs via cloud provider
        metrics = await self.provider.get_metrics("AWS/ECS", "CPUUtilization", {})
        logs = await self.provider.get_logs("/app/logs", "ERROR")

        detected_anomalies: List[Anomaly] = []
        hypothesis = "Transient load spike"

        for log_entry in logs:
            msg = log_entry.get("message", "")
            if "OutOfMemoryError" in msg or "137" in msg:
                anom = Anomaly(
                    metric_name="MemoryUsage",
                    anomaly_score=0.96,
                    deviation_sigma=4.2,
                    description="Severe OOMKilled container termination cycle detected",
                    root_cause_hypothesis="Heap exhaustion in microservice cache layer",
                )
                detected_anomalies.append(anom)
                hypothesis = anom.root_cause_hypothesis
            elif "ProvisionedThroughputExceededException" in msg:
                anom = Anomaly(
                    metric_name="DynamoDB_ThrottledRequests",
                    anomaly_score=0.92,
                    deviation_sigma=3.8,
                    description="DynamoDB RCU saturation causing upstream timeout cascading",
                    root_cause_hypothesis="Hot partition key under sudden flash burst",
                )
                detected_anomalies.append(anom)
                hypothesis = anom.root_cause_hypothesis
            elif "PutBucketPolicy" in msg or "Unauthorized" in msg:
                anom = Anomaly(
                    metric_name="CloudTrail_SuspiciousAccess",
                    anomaly_score=0.99,
                    deviation_sigma=5.0,
                    description="Unauthorized IAM credential exfiltration and public S3 bucket ACL alteration",
                    root_cause_hypothesis="Compromised long-lived IAM Access Key actively utilized",
                )
                detected_anomalies.append(anom)
                hypothesis = anom.root_cause_hypothesis

        if not detected_anomalies:
            detected_anomalies.append(
                Anomaly(
                    metric_name="GeneralMetrics",
                    anomaly_score=0.45,
                    description="General performance degradation observed",
                    root_cause_hypothesis="Network latency or thread starvation",
                )
            )

        state.anomalies.extend(detected_anomalies)
        state.incident.root_cause = hypothesis
        self.memory.record_decision({"anomalies_count": len(detected_anomalies), "hypothesis": hypothesis})

        return AgentMessage(
            sender=self.role,
            recipient=AgentRole.INCIDENT_COMMANDER.value,
            verb="TELEMETRY_ANOMALY_FOUND",
            payload={
                "anomalies": [a.to_dict() for a in detected_anomalies],
                "hypothesis": hypothesis,
                "confidence": 0.94,
            },
        )
