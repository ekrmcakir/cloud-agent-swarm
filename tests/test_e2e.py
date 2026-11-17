import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
from cloud_agent_swarm.connectors.mock_provider import MockCloudProvider
from cloud_agent_swarm.scenarios.catalog import SCENARIO_CATALOG, get_scenario
from cloud_agent_swarm.swarm.coordinator import SwarmCoordinator
from cloud_agent_swarm.core.models import Incident, IncidentStatus

class TestEndToEnd(unittest.IsolatedAsyncioTestCase):
    async def test_full_incident_chaos_lifecycle_all_scenarios(self):
        provider = MockCloudProvider()

        for scenario_id, scen in SCENARIO_CATALOG.items():
            with self.subTest(scenario=scenario_id):
                provider.set_scenario(scenario_id, {})
                coordinator = SwarmCoordinator(provider)

                incident = Incident(
                    title=scen.name,
                    description=scen.description,
                    severity=scen.severity,
                    affected_services=[scen.target_service],
                )

                state = await coordinator.execute_swarm_loop(incident)

                self.assertTrue(state.is_completed)
                self.assertEqual(state.incident.status, IncidentStatus.MITIGATED)
                self.assertIsNotNone(state.postmortem_markdown)
                self.assertGreater(len(state.anomalies), 0)
                self.assertIsNotNone(state.blast_radius)
                self.assertIsNotNone(state.remediation_plan)
                self.assertEqual(state.remediation_plan.execution_status, "SUCCESS")

if __name__ == "__main__":
    unittest.main()
