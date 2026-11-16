import json
import asyncio
from typing import Dict, Any
from ..connectors.mock_provider import MockCloudProvider
from ..scenarios.catalog import SCENARIO_CATALOG, get_scenario
from ..swarm.coordinator import SwarmCoordinator
from ..core.models import Incident

# Lightweight standalone web application
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
    <h3>Active Incident: Kubernetes OOMKilled Cascading CrashLoop</h3>
    <p>Severity: <span class="sev1">SEV-1</span> | Status: <span style="color:#7ee787">MITIGATED</span></p>
    <p>Root Cause: <em>Heap exhaustion in microservice cache layer</em></p>
  </div>
  <div class="card">
    <h3>Agent Swarm Consensus Log</h3>
    <pre>
[incident_commander]     -> TRIAGE_RESPONSE          to: all
[telemetry_investigator] -> TELEMETRY_ANOMALY_FOUND  to: incident_commander
[blast_radius_analyst]   -> BLAST_RADIUS_EVALUATED   to: incident_commander
[remediation_planner]    -> PROPOSE_REMEDIATION      to: incident_commander
[incident_commander]     -> INCIDENT_RESOLVED        to: all
    </pre>
  </div>
</body>
</html>
"""

class WarRoomApp:
    def __init__(self):
        self.html = HTML_PAGE

    def get_index_html(self) -> str:
        return self.html

app = WarRoomApp()
