import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
from cloud_agent_swarm.core.models import Incident, Severity, IncidentStatus, SwarmState
from cloud_agent_swarm.connectors.mock_provider import MockCloudProvider
from cloud_agent_swarm.agents.telemetry_investigator import TelemetryInvestigatorAgent
from cloud_agent_swarm.agents.blast_radius_analyst import BlastRadiusAnalystAgent
from cloud_agent_swarm.agents.remediation_planner import RemediationPlannerAgent
from cloud_agent_swarm.agents.incident_commander import IncidentCommanderAgent

class TestAgents(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_provider = MockCloudProvider()
        self.incident = Incident(
            title="Checkout Pod OOM Outage",
            description="502 Bad Gateway across checkout fleet",
            severity=Severity.SEV1,
            affected_services=["checkout-service"],
        )
        self.state = SwarmState(incident=self.incident)

    async def test_telemetry_investigator_oom_detection(self):
        self.mock_provider.set_scenario("OOMKilled_Cascade", {})
        investigator = TelemetryInvestigatorAgent(self.mock_provider)
        msg = await investigator.process_turn(self.state)

        self.assertEqual(msg.verb, "TELEMETRY_ANOMALY_FOUND")
        self.assertGreater(len(self.state.anomalies), 0)
        self.assertIn("Heap exhaustion", self.state.incident.root_cause)

    async def test_blast_radius_evaluation(self):
        self.state.incident.root_cause = "Compromised long-lived IAM Access Key"
        blast_agent = BlastRadiusAnalystAgent()
        msg = await blast_agent.process_turn(self.state)

        self.assertEqual(msg.verb, "BLAST_RADIUS_EVALUATED")
        self.assertIsNotNone(self.state.blast_radius)
        self.assertTrue(self.state.blast_radius.requires_human_approval)
        self.assertGreater(self.state.blast_radius.risk_score, 70.0)

if __name__ == "__main__":
    unittest.main()
