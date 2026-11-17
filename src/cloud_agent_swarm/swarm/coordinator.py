import asyncio
import time
from typing import Dict, Any, List, Optional
from ..core.models import (
    SwarmState, Incident, IncidentStatus, AgentRole, AgentMessage
)
from ..core.event_bus import EventBus
from ..connectors.base import BaseCloudProvider
from ..agents.incident_commander import IncidentCommanderAgent
from ..agents.telemetry_investigator import TelemetryInvestigatorAgent
from ..agents.blast_radius_analyst import BlastRadiusAnalystAgent
from ..agents.remediation_planner import RemediationPlannerAgent
from .guardrails import GuardrailEnforcer, GuardrailViolation
from .hitl import HITLCheckpoint, ApprovalDecision
from .postmortem import PostMortemGenerator
from .graph import SwarmGraph

class SwarmCoordinator:
    """High-performance multi-agent swarm coordinator orchestrating the incident lifecycle."""

    def __init__(
        self,
        cloud_provider: BaseCloudProvider,
        hitl: Optional[HITLCheckpoint] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.provider = cloud_provider
        self.commander = IncidentCommanderAgent()
        self.investigator = TelemetryInvestigatorAgent(cloud_provider)
        self.blast_analyst = BlastRadiusAnalystAgent()
        self.remediation_planner = RemediationPlannerAgent()
        self.guardrails = GuardrailEnforcer()
        self.hitl = hitl or HITLCheckpoint(auto_approve=True)
        self.postmortem_gen = PostMortemGenerator()
        self.event_bus = event_bus or EventBus()
        self.message_history: List[AgentMessage] = []
        self.execution_audit_trail: List[Dict[str, Any]] = []

    async def execute_swarm_loop(self, incident: Incident) -> SwarmState:
        t0 = time.time()
        state = SwarmState(incident=incident)
        await self._audit("SWARM_INITIALIZED", {"incident_id": incident.id, "severity": incident.severity.value})

        # Stage 1: Commander Triage
        msg_triage = await self.commander.process_turn(state)
        await self._record_message(state, msg_triage)
        await self._audit("TRIAGE_COMPLETED", {"status": state.incident.status.value})

        # Stage 2: Sequential Investigation & Blast Radius Assessment (Pipeline to avoid race condition)
        msg_invest = await self.investigator.process_turn(state)
        await self._record_message(state, msg_invest)
        
        msg_blast = await self.blast_analyst.process_turn(state)
        await self._record_message(state, msg_blast)

        await self._audit("ANALYSIS_COMPLETED", {
            "root_cause": state.incident.root_cause,
            "risk_score": state.blast_radius.risk_score if state.blast_radius else None,
        })

        # Stage 3: Remediation Planning
        msg_plan = await self.remediation_planner.process_turn(state)
        await self._record_message(state, msg_plan)

        # Stage 4: Guardrail Verification
        if state.remediation_plan:
            try:
                for action in state.remediation_plan.actions:
                    self.guardrails.verify_action(action)
                await self._audit("GUARDRAILS_PASSED", {"action_count": len(state.remediation_plan.actions)})
            except GuardrailViolation as gv:
                state.incident.status = IncidentStatus.ABORTED
                state.remediation_plan.execution_status = "ABORTED_GUARDRAIL_VIOLATION"
                await self._audit("GUARDRAILS_VIOLATION", {"error": str(gv)})
                state.postmortem_markdown = self.postmortem_gen.generate(state)
                state.is_completed = True
                return state

        # Stage 5: Human-in-the-Loop Checkpoint
        if state.remediation_plan and state.remediation_plan.requires_human_approval:
            state.incident.status = IncidentStatus.AWAITING_APPROVAL
            approval = await self.hitl.request_approval(state.remediation_plan)
            if approval.decision == ApprovalDecision.APPROVED:
                state.remediation_plan.approved_by = approval.approved_by or "operator"
                await self._audit("HITL_APPROVED", {"approved_by": state.remediation_plan.approved_by})
            else:
                state.incident.status = IncidentStatus.ABORTED
                await self._audit("HITL_REJECTED", {"reason": approval.reason})
                state.postmortem_markdown = self.postmortem_gen.generate(state)
                state.is_completed = True
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
            await self._audit("REMEDIATION_EXECUTED", {"actions": len(state.remediation_plan.actions)})

        # Stage 7: Commander Final Resolution
        msg_resolve = await self.commander.process_turn(state)
        await self._record_message(state, msg_resolve)

        # Stage 8: Post-Mortem Generation
        state.postmortem_markdown = self.postmortem_gen.generate(state)
        state.is_completed = True
        await self._audit("SWARM_COMPLETED", {"elapsed_seconds": round(time.time() - t0, 3)})
        return state

    async def _record_message(self, state: SwarmState, msg: AgentMessage):
        state.messages.append(msg)
        self.message_history.append(msg)
        await self.event_bus.publish(
            topic=f"swarm.agent.{msg.sender.value}",
            payload=msg.to_dict(),
        )

    async def _audit(self, event_name: str, payload: Dict[str, Any]):
        entry = {
            "event": event_name,
            "timestamp": time.time(),
            "payload": payload,
        }
        self.execution_audit_trail.append(entry)
        await self.event_bus.publish(
            topic=f"swarm.audit.{event_name.lower()}",
            payload=entry,
        )

    def build_graph(self) -> SwarmGraph:
        """Constructs declarative SwarmGraph for state-machine based incident resolution."""
        graph = SwarmGraph()

        async def node_triage(state: SwarmState) -> SwarmState:
            msg = await self.commander.process_turn(state)
            await self._record_message(state, msg)
            return state

        async def node_investigate(state: SwarmState) -> SwarmState:
            msg = await self.investigator.process_turn(state)
            await self._record_message(state, msg)
            return state

        async def node_blast_radius(state: SwarmState) -> SwarmState:
            msg = await self.blast_analyst.process_turn(state)
            await self._record_message(state, msg)
            return state

        async def node_plan(state: SwarmState) -> SwarmState:
            msg = await self.remediation_planner.process_turn(state)
            await self._record_message(state, msg)
            return state

        async def node_guardrails(state: SwarmState) -> SwarmState:
            if state.remediation_plan:
                try:
                    for action in state.remediation_plan.actions:
                        self.guardrails.verify_action(action)
                except GuardrailViolation as gv:
                    state.incident.status = IncidentStatus.ABORTED
                    state.remediation_plan.execution_status = "ABORTED_GUARDRAIL_VIOLATION"
                    await self._audit("GUARDRAILS_VIOLATION", {"error": str(gv)})
            return state

        async def node_hitl(state: SwarmState) -> SwarmState:
            if state.remediation_plan and state.remediation_plan.requires_human_approval:
                state.incident.status = IncidentStatus.AWAITING_APPROVAL
                approval = await self.hitl.request_approval(state.remediation_plan)
                if approval.decision == ApprovalDecision.APPROVED:
                    state.remediation_plan.approved_by = approval.approved_by or "operator"
                else:
                    state.incident.status = IncidentStatus.ABORTED
            return state

        async def node_execution(state: SwarmState) -> SwarmState:
            if state.remediation_plan and state.incident.status != IncidentStatus.ABORTED:
                for action in state.remediation_plan.actions:
                    await self.provider.execute_action(
                        action_type=action.action_type,
                        resource_id=action.target_resource,
                        parameters=action.parameters,
                    )
                state.remediation_plan.execution_status = "SUCCESS"
            return state

        async def node_resolve(state: SwarmState) -> SwarmState:
            if state.incident.status != IncidentStatus.ABORTED:
                msg = await self.commander.process_turn(state)
                await self._record_message(state, msg)
            state.postmortem_markdown = self.postmortem_gen.generate(state)
            state.is_completed = True
            return state

        graph.add_node("triage", node_triage)
        graph.add_node("investigate", node_investigate)
        graph.add_node("blast_radius", node_blast_radius)
        graph.add_node("plan", node_plan)
        graph.add_node("guardrails", node_guardrails)
        graph.add_node("hitl", node_hitl)
        graph.add_node("execution", node_execution)
        graph.add_node("resolve", node_resolve)

        graph.add_transition("triage", "default", "investigate")
        graph.add_transition("investigate", "default", "blast_radius")
        graph.add_transition("blast_radius", "default", "plan")
        graph.add_transition("plan", "default", "guardrails")
        graph.add_transition("guardrails", "aborted", "resolve")
        graph.add_transition("guardrails", "default", "hitl")
        graph.add_transition("hitl", "aborted", "resolve")
        graph.add_transition("hitl", "default", "execution")
        graph.add_transition("execution", "default", "resolve")
        graph.add_transition("resolve", "default", "end")

        return graph

    async def execute_swarm_graph(self, incident: Incident) -> SwarmState:
        """Executes the incident lifecycle using the declarative SwarmGraph state machine."""
        state = SwarmState(incident=incident)
        graph = self.build_graph()
        return await graph.run(state, start_node="triage")
