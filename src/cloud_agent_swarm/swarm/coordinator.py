import asyncio
import time
from typing import Dict, Any, List, Optional
from ..core.models import (
    SwarmState, Incident, IncidentStatus, AgentRole, AgentMessage
)
from ..connectors.base import BaseCloudProvider
from ..agents.incident_commander import IncidentCommanderAgent
from ..agents.telemetry_investigator import TelemetryInvestigatorAgent
from ..agents.blast_radius_analyst import BlastRadiusAnalystAgent
from ..agents.remediation_planner import RemediationPlannerAgent
from .guardrails import GuardrailEnforcer
from .hitl import HITLCheckpoint, ApprovalDecision
from .postmortem import PostMortemGenerator

class SwarmCoordinator:
    """High-performance multi-agent swarm coordinator orchestrating the incident lifecycle."""

    def __init__(self, cloud_provider: BaseCloudProvider, hitl: Optional[HITLCheckpoint] = None):
        self.provider = cloud_provider
        self.commander = IncidentCommanderAgent()
        self.investigator = TelemetryInvestigatorAgent(cloud_provider)
        self.blast_analyst = BlastRadiusAnalystAgent()
        self.remediation_planner = RemediationPlannerAgent()
        self.guardrails = GuardrailEnforcer()
        self.hitl = hitl or HITLCheckpoint(auto_approve=True)
        self.postmortem_gen = PostMortemGenerator()
        self.message_history: List[AgentMessage] = []

    async def execute_swarm_loop(self, incident: Incident) -> SwarmState:
        state = SwarmState(incident=incident)

        # Stage 1: Commander Triage
        msg_triage = await self.commander.process_turn(state)
        self._record_message(state, msg_triage)

        # Stage 2: Parallel Investigation & Blast Radius Assessment
        t_investigation = asyncio.create_task(self.investigator.process_turn(state))
        t_blast = asyncio.create_task(self.blast_analyst.process_turn(state))
        msg_invest, msg_blast = await asyncio.gather(t_investigation, t_blast)
        self._record_message(state, msg_invest)
        self._record_message(state, msg_blast)

        # Stage 3: Remediation Planning
        msg_plan = await self.remediation_planner.process_turn(state)
        self._record_message(state, msg_plan)

        # Stage 4: Guardrail Verification
        if state.remediation_plan:
            for action in state.remediation_plan.actions:
                self.guardrails.verify_action(action)

        # Stage 5: Human-in-the-Loop Checkpoint
        if state.remediation_plan and state.remediation_plan.requires_human_approval:
            state.incident.status = IncidentStatus.AWAITING_APPROVAL
            approval = await self.hitl.request_approval(state.remediation_plan)
            if approval.decision == ApprovalDecision.APPROVED:
                state.remediation_plan.approved_by = approval.approved_by or "operator"
            else:
                state.incident.status = IncidentStatus.ABORTED
                return state

        # Stage 6: Safe Execution
        if state.remediation_plan:
            for action in state.remediation_plan.actions:
                await self.provider.execute_action(
                    action_type=action.action_type,
                    resource_id=action.target_resource,
                    parameters=action.parameters,
                )
            state.remediation_plan.execution_status = "SUCCESS"

        # Stage 7: Commander Final Resolution
        msg_resolve = await self.commander.process_turn(state)
        self._record_message(state, msg_resolve)

        # Stage 8: Post-Mortem Generation
        state.postmortem_markdown = self.postmortem_gen.generate(state)
        state.is_completed = True
        return state

    def _record_message(self, state: SwarmState, msg: AgentMessage):
        state.messages.append(msg)
        self.message_history.append(msg)
