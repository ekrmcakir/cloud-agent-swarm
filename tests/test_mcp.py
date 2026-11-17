import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
import json
from cloud_agent_swarm.mcp_server.tools import SwarmMCPTools
from cloud_agent_swarm.mcp_server.server import create_mcp_server

class TestMCP(unittest.IsolatedAsyncioTestCase):
    async def test_mcp_tools(self):
        tools = SwarmMCPTools()
        scenarios = await tools.list_available_scenarios()
        self.assertGreater(len(scenarios), 0)

        result = await tools.trigger_incident_investigation("oom_cascade")
        self.assertEqual(result["status"], "MITIGATED")
        self.assertIsNotNone(result["root_cause"])

        postmortem = await tools.get_latest_postmortem()
        self.assertIn("Post-Mortem", postmortem)

    async def test_mcp_server_json_rpc(self):
        server = create_mcp_server()
        req_list = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        res_list = await server.handle_request(req_list)
        self.assertEqual(res_list["id"], 1)
        self.assertIn("tools", res_list["result"])

        # Test initialize
        req_init = {"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {}}
        res_init = await server.handle_request(req_init)
        self.assertEqual(res_init["id"], 2)
        self.assertIn("protocolVersion", res_init["result"])

        # Test ping
        req_ping = {"jsonrpc": "2.0", "id": 3, "method": "ping", "params": {}}
        res_ping = await server.handle_request(req_ping)
        self.assertEqual(res_ping["id"], 3)

if __name__ == "__main__":
    unittest.main()
