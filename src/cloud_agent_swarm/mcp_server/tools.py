from typing import Dict, Any, List
from ..core.models import Incident, Severity, IncidentStatus
from ..connectors.mock_provider import MockCloudProvider
from ..scenarios.catalog import get_scenario, SCENARIO_CATALOG
from ..swarm.coordinator import SwarmCoordinator

class SwarmMCPTools:
    """Model Context Protocol (MCP) Tool handlers allowing AI assistants to drive the swarm."""

    def __init__(self):
        self.provider = MockCloudProvider()
        self.coordinator = SwarmCoordinator(self.provider)
        self.last_state = None

    async def list_available_scenarios(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": s.id,
                "name": s.name,
                "severity": s.severity.value,
                "description": s.description,
            }
            for s in SCENARIO_CATALOG.values()
        ]

    async def trigger_incident_investigation(self, scenario_id: str) -> Dict[str, Any]:
        scen = get_scenario(scenario_id)
        if not scen:
            return {"error": f"Scenario '{scenario_id}' not found"}

        self.provider.set_scenario(scenario_id, {})
        incident = Incident(
            title=scen.name,
            description=scen.description,
            severity=scen.severity,
            affected_services=[scen.target_service],
        )

        state = await self.coordinator.execute_swarm_loop(incident)
        self.last_state = state

        return {
            "incident_id": state.incident.id,
            "status": state.incident.status.value,
            "root_cause": state.incident.root_cause,
            "blast_radius_risk": state.blast_radius.risk_score if state.blast_radius else None,
            "actions_executed": len(state.remediation_plan.actions) if state.remediation_plan else 0,
            "postmortem_preview": state.postmortem_markdown[:250] + "..." if state.postmortem_markdown else None,
        }

    async def get_latest_postmortem(self) -> str:
        if not self.last_state or not self.last_state.postmortem_markdown:
            return "No post-mortem report available. Run an incident investigation first."
        return self.last_state.postmortem_markdown
