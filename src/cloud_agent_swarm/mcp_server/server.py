import json
import sys
import asyncio
from typing import Dict, Any
from .tools import SwarmMCPTools

class JSONRPCMCPServer:
    """Standard JSON-RPC 2.0 stdio server compliant with Anthropic/Model Context Protocol."""

    def __init__(self):
        self.tools = SwarmMCPTools()

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "cloud-agent-swarm", "version": "1.0.0"},
                },
            }
        elif method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "list_scenarios",
                            "description": "List all runnable cloud chaos incident scenarios.",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                        {
                            "name": "trigger_investigation",
                            "description": "Trigger the autonomous multi-agent swarm on a cloud incident.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"scenario_id": {"type": "string"}},
                                "required": ["scenario_id"],
                            },
                        },
                        {
                            "name": "get_postmortem",
                            "description": "Retrieve the latest SRE incident post-mortem markdown report.",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                    ]
                },
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})

            if tool_name == "list_scenarios":
                res = await self.tools.list_available_scenarios()
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
            elif tool_name == "trigger_investigation":
                res = await self.tools.trigger_incident_investigation(args.get("scenario_id", "oom_cascade"))
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
            elif tool_name == "get_postmortem":
                res = await self.tools.get_latest_postmortem()
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": res}]}}
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}

        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid request"}}

    async def run_stdio(self):
        """Asynchronous stdio event loop processing line-delimited JSON-RPC messages."""
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break
            raw = line.decode("utf-8").strip()
            if not raw:
                continue
            try:
                request = json.loads(raw)
                response = await self.handle_request(request)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

def create_mcp_server() -> JSONRPCMCPServer:
    return JSONRPCMCPServer()
