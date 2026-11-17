import json
import asyncio
from typing import Dict, Any, Optional
from ..connectors.mock_provider import MockCloudProvider
from ..scenarios.catalog import SCENARIO_CATALOG, get_scenario
from ..swarm.coordinator import SwarmCoordinator
from ..core.models import Incident

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CloudAgentSwarm War Room</title>
  <style>
    body { background-color: #0d1117; color: #c9d1d9; font-family: monospace; padding: 2rem; }
    h1 { color: #58a6ff; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; }
    .sev1 { color: #ff7b72; font-weight: bold; }
    .btn { background: #238636; color: white; padding: 0.5rem 1rem; border: none; border-radius: 6px; cursor: pointer; }
    pre { background: #0d1117; padding: 1rem; border: 1px solid #30363d; overflow: auto; }
  </style>
</head>
<body>
  <h1>⚡ CloudAgentSwarm — Incident War Room</h1>
  <div class="card">
    <h3>Autonomous Multi-Agent Cloud SRE Cockpit</h3>
    <p>Status: <span style="color:#7ee787">READY</span></p>
    <p>Endpoints: <code>/api/scenarios</code>, <code>/api/trigger/{scenario_id}</code>, <code>/api/postmortem</code></p>
  </div>
</body>
</html>
"""

def create_web_app():
    if not FASTAPI_AVAILABLE:
        class StandaloneWarRoomApp:
            def __init__(self):
                self.html = HTML_PAGE
            def get_index_html(self) -> str:
                return self.html
        return StandaloneWarRoomApp()

    api = FastAPI(title="CloudAgentSwarm API", version="1.0.0")
    provider = MockCloudProvider()
    coordinator = SwarmCoordinator(provider)
    last_state = {"state": None}

    @api.get("/", response_class=HTMLResponse)
    async def index():
        return HTML_PAGE

    @api.get("/api/scenarios")
    async def list_scenarios():
        return [
            {
                "id": s.id,
                "name": s.name,
                "severity": s.severity.value,
                "description": s.description,
            }
            for s in SCENARIO_CATALOG.values()
        ]

    @api.post("/api/trigger/{scenario_id}")
    async def trigger(scenario_id: str):
        scen = get_scenario(scenario_id)
        if not scen:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

        provider.set_scenario(scenario_id, {})
        incident = Incident(
            title=scen.name,
            description=scen.description,
            severity=scen.severity,
            affected_services=[scen.target_service],
        )
        state = await coordinator.execute_swarm_loop(incident)
        last_state["state"] = state
        return state.to_dict()

    @api.get("/api/postmortem")
    async def get_postmortem():
        st = last_state.get("state")
        if not st or not st.postmortem_markdown:
            raise HTTPException(status_code=404, detail="No post-mortem report available")
        return {"postmortem_markdown": st.postmortem_markdown}

    return api

app = create_web_app()
