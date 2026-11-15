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

if __name__ == "__main__":
    unittest.main()
