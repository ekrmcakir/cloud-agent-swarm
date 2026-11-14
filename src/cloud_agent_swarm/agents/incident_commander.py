import time
from .base import BaseAgent
from ..core.models import (
    AgentRole, AgentMessage, SwarmState, Severity, IncidentStatus
)

class IncidentCommanderAgent(BaseAgent):
    """Root coordinator agent responsible for triage, consensus, and delegation."""

    def __init__(self):
        super().__init__(
            role=AgentRole.INCIDENT_COMMANDER,
            name="Commander-Prime",
            system_prompt=(
                "You are the Incident Commander. You lead the multi-agent incident war-room. "
                "Assess severity, delegate investigation tasks to specialized agents, "
                "orchestrate consensus, and authorize remediation."
            ),
        )

    async def process_turn(self, state: SwarmState) -> AgentMessage:
        self.log(f"Commander evaluating state (Iteration {state.iteration_count})")

        if state.incident.status == IncidentStatus.DETECTED:
            # Triage step
            state.incident.status = IncidentStatus.TRIAGING
            if any(k in state.incident.title for k in ("OOM", "Security", "Leak", "Compromise", "Exfiltration")):
                state.incident.severity = Severity.SEV1
            else:
                state.incident.severity = Severity.SEV2

            self.log(f"Incident triaged as {state.incident.severity.value}. Delegating investigation.")
            return AgentMessage(
                sender=self.role,
                recipient="all",
                verb="TRIAGE_RESPONSE",
                payload={"severity": state.incident.severity.value, "next": "INVESTIGATE"},
            )

        if state.anomalies and not state.blast_radius:
            return AgentMessage(
                sender=self.role,
                recipient=AgentRole.BLAST_RADIUS_ANALYST.value,
                verb="BLAST_RADIUS_REQUEST",
                payload={"incident_id": state.incident.id},
            )

        if state.blast_radius and not state.remediation_plan:
            return AgentMessage(
                sender=self.role,
                recipient=AgentRole.REMEDIATION_PLANNER.value,
                verb="PROPOSE_REMEDIATION",
                payload={"blast_risk": state.blast_radius.risk_score},
            )

        if state.remediation_plan:
            if state.remediation_plan.requires_human_approval and not state.remediation_plan.approved_by:
                state.incident.status = IncidentStatus.AWAITING_APPROVAL
                return AgentMessage(
                    sender=self.role,
                    recipient="human_operator",
                    verb="APPROVAL_REQUEST",
                    payload={"plan_id": state.remediation_plan.id, "risk": state.remediation_plan.total_risk_score},
                )
            else:
                state.incident.status = IncidentStatus.MITIGATED
                state.incident.resolved_at = time.time()
                return AgentMessage(
                    sender=self.role,
                    recipient="all",
                    verb="INCIDENT_RESOLVED",
                    payload={"incident_id": state.incident.id, "status": "MITIGATED"},
                )

        return AgentMessage(
            sender=self.role,
            recipient="all",
            verb="CONSENSUS_VOTE",
            payload={"status": "IN_PROGRESS"},
        )
