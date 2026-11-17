import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
from cloud_agent_swarm.core.models import Incident, Severity, IncidentStatus, RemediationAction
from cloud_agent_swarm.connectors.mock_provider import MockCloudProvider
from cloud_agent_swarm.swarm.coordinator import SwarmCoordinator
from cloud_agent_swarm.swarm.guardrails import GuardrailEnforcer, GuardrailViolation
from cloud_agent_swarm.swarm.hitl import HITLCheckpoint, ApprovalDecision

class TestSwarm(unittest.IsolatedAsyncioTestCase):
    async def test_full_swarm_coordinator_flow(self):
        mock_provider = MockCloudProvider()
        mock_provider.set_scenario("OOMKilled_Cascade", {})
        coordinator = SwarmCoordinator(mock_provider)

        incident = Incident(
            title="Checkout Outage OOM",
            description="502 Bad Gateway",
            severity=Severity.SEV1,
            affected_services=["checkout-api"],
        )

        state = await coordinator.execute_swarm_loop(incident)

        self.assertTrue(state.is_completed)
        self.assertEqual(state.incident.status, IncidentStatus.MITIGATED)
        self.assertIsNotNone(state.postmortem_markdown)
        self.assertIn("Post-Mortem", state.postmortem_markdown)
        self.assertGreater(len(state.messages), 3)

    def test_guardrails_blocks_destructive_forbidden_action(self):
        enforcer = GuardrailEnforcer(max_replicas_limit=20)
        forbidden_act = RemediationAction(
            action_type="drop_database",
            target_resource="production-rds",
            risk_level="CRITICAL",
        )
        with self.assertRaises(GuardrailViolation):
            enforcer.verify_action(forbidden_act)

        scale_overflow = RemediationAction(
            action_type="scale_deployment",
            target_resource="checkout",
            parameters={"replicas": 100},
            risk_level="LOW",
        )
        with self.assertRaises(GuardrailViolation):
            enforcer.verify_action(scale_overflow)

    async def test_swarm_graph_execution(self):
        mock_provider = MockCloudProvider()
        mock_provider.set_scenario("OOMKilled_Cascade", {})
        coordinator = SwarmCoordinator(mock_provider)

        incident = Incident(
            title="Graph Checkout Outage OOM",
            description="502 Bad Gateway",
            severity=Severity.SEV1,
            affected_services=["checkout-api"],
        )

        state = await coordinator.execute_swarm_graph(incident)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.incident.status, IncidentStatus.MITIGATED)
        self.assertIsNotNone(state.postmortem_markdown)

    async def test_guardrail_violation_aborts_gracefully(self):
        mock_provider = MockCloudProvider()
        mock_provider.set_scenario("OOMKilled_Cascade", {})
        coordinator = SwarmCoordinator(mock_provider)
        # Limit max replicas to 1 so the planner's action (replicas=4) triggers violation
        coordinator.guardrails = GuardrailEnforcer(max_replicas_limit=1)

        incident = Incident(
            title="Checkout Outage OOM",
            description="502 Bad Gateway",
            severity=Severity.SEV1,
            affected_services=["checkout-api"],
        )

        state = await coordinator.execute_swarm_loop(incident)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.incident.status, IncidentStatus.ABORTED)
        self.assertEqual(state.remediation_plan.execution_status, "ABORTED_GUARDRAIL_VIOLATION")
        self.assertIsNotNone(state.postmortem_markdown)

    async def test_event_bus_integration(self):
        from cloud_agent_swarm.core.event_bus import EventBus
        bus = EventBus()
        captured_events = []

        async def capture_event(evt):
            captured_events.append(evt)

        bus.subscribe("swarm.agent.*", capture_event)
        bus.subscribe("swarm.audit.*", capture_event)

        mock_provider = MockCloudProvider()
        mock_provider.set_scenario("OOMKilled_Cascade", {})
        coordinator = SwarmCoordinator(mock_provider, event_bus=bus)

        incident = Incident(
            title="EventBus Test Incident",
            severity=Severity.SEV2,
            affected_services=["checkout-api"],
        )
        await coordinator.execute_swarm_loop(incident)
        self.assertGreater(len(captured_events), 5)

if __name__ == "__main__":
    unittest.main()
