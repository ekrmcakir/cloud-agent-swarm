# Model Context Protocol (MCP) Specification

`CloudAgentSwarm` exposes a standard MCP 2.x interface over stdio, allowing IDEs (Claude Code, Cursor, Antigravity) to orchestrate cloud incident responses.

## Exposed MCP Tools
1. `list_scenarios`: Enumerate available test scenarios.
2. `trigger_investigation`: Spawns the multi-agent swarm on an incident.
3. `get_postmortem`: Pulls the rendered GitHub markdown post-mortem.

## Stdio JSON-RPC Usage
```bash
python3 -m cloud_agent_swarm.cli.main mcp
```
