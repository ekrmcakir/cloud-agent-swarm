import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
from cloud_agent_swarm.core.models import Incident, Severity, IncidentStatus, SwarmState
from cloud_agent_swarm.cli.tui import render_swarm_run
from cloud_agent_swarm.cli.interactive_hitl import prompt_human_operator_terminal
from cloud_agent_swarm.core.models import RemediationPlan, RemediationAction

class TestCLI(unittest.TestCase):
    def test_tui_render(self):
        inc = Incident(title="Test Incident", severity=Severity.SEV2, status=IncidentStatus.MITIGATED)
        state = SwarmState(incident=inc)
        # Verify render does not crash
        render_swarm_run(state, output_json=False)
        render_swarm_run(state, output_json=True)

    def test_interactive_hitl_non_interactive(self):
        plan = RemediationPlan(
            incident_id="inc-1",
            actions=[RemediationAction(action_type="scale_deployment", risk_level="LOW")],
            total_risk_score=20.0
        )
        verdict = prompt_human_operator_terminal(plan, auto_approve=True)
        self.assertIsNotNone(verdict)

if __name__ == "__main__":
    unittest.main()
