import time
from typing import Dict, Any

class SwarmTelemetryRecorder:
    """OpenTelemetry metric recorder tracking swarm consensus latency and resolution MTTR."""

    def __init__(self):
        self.recorded_metrics: Dict[str, float] = {}

    def record_decision_latency(self, agent_role: str, latency_seconds: float):
        key = f"swarm.decision_latency.{agent_role}"
        self.recorded_metrics[key] = latency_seconds

    def record_incident_resolved(self, incident_id: str, mttr_seconds: float):
        self.recorded_metrics[f"swarm.incident_mttr.{incident_id}"] = mttr_seconds
