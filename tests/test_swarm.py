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

if __name__ == "__main__":
    unittest.main()
