import time
from .base import BaseAgent
from ..core.models import AgentRole, AgentMessage, SwarmState, BlastRadiusReport

class BlastRadiusAnalystAgent(BaseAgent):
    """Assesses safety perimeter, IAM privilege escalation risks, and blast radius of failures."""

    def __init__(self):
        super().__init__(
            role=AgentRole.BLAST_RADIUS_ANALYST,
            name="Blast-Radius-Sentinel",
            system_prompt=(
                "You are an enterprise Cloud Security & Reliability Blast Radius Analyst. "
                "Assess whether incidents cross VPC boundaries, expose customer data, "
                "risk cascading outages, or require Human-in-the-Loop approval."
            ),
        )

    async def process_turn(self, state: SwarmState) -> AgentMessage:
        self.log(f"Evaluating blast radius for incident {state.incident.id}")

        hypothesis = state.incident.root_cause or "Unknown"
        risk_score = 20.0
        vpc_crossed = False
        requires_hitl = False
        affected_components = list(state.incident.affected_services) or ["app-gateway"]
        reasoning = "Contained failure within isolated microservice boundary."

        if "IAM" in hypothesis or "Compromised" in hypothesis or "exfiltration" in hypothesis:
            risk_score = 88.0
            vpc_crossed = True
            requires_hitl = True
            affected_components.extend(["iam-role-admin", "s3-customer-bucket", "kms-key-vault"])
            reasoning = "CRITICAL: Security boundary breached. Unauthorized entity possesses IAM access."
        elif "OOMKilled" in hypothesis or "Heap" in hypothesis:
            risk_score = 35.0
            requires_hitl = False
            affected_components.append("checkout-pod-replicas")
            reasoning = "Application pod crashloop contained to stateless Kubernetes deployment."
        elif "DynamoDB" in hypothesis or "Throttling" in hypothesis:
            risk_score = 45.0
            requires_hitl = True
            affected_components.append("dynamodb-orders-table")
            reasoning = "Persistent data store throttling causing queuing upstream."

        report = BlastRadiusReport(
            incident_id=state.incident.id,
            risk_score=risk_score,
            affected_components=affected_components,
            iam_roles_at_risk=["arn:aws:iam::123456789012:role/Admin"] if risk_score > 70 else [],
            vpc_boundaries_crossed=vpc_crossed,
            financial_exposure_usd=15000.0 if risk_score > 70 else 250.0,
            requires_human_approval=requires_hitl,
            reasoning=reasoning,
        )

        state.blast_radius = report
        self.memory.record_decision(report.to_dict())

        return AgentMessage(
            sender=self.role,
            recipient=AgentRole.INCIDENT_COMMANDER.value,
            verb="BLAST_RADIUS_EVALUATED",
            payload=report.to_dict(),
        )
