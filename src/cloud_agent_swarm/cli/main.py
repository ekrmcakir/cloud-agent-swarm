import argparse
import asyncio
import sys
from ..connectors.mock_provider import MockCloudProvider
from ..scenarios.catalog import SCENARIO_CATALOG, get_scenario
from ..swarm.coordinator import SwarmCoordinator
from ..core.models import Incident, Severity
from .tui import render_swarm_run

def parse_args():
    parser = argparse.ArgumentParser(
        prog="cloud-swarm",
        description="CloudAgentSwarm - Autonomous Multi-Agent Cloud SRE & Incident Commander",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # simulate command
    sim_parser = subparsers.add_parser("simulate", help="Run multi-agent swarm on a simulated incident")
    sim_parser.add_argument(
        "--scenario",
        default="oom_cascade",
        choices=list(SCENARIO_CATALOG.keys()),
        help="Predefined chaos scenario to inject",
    )
    sim_parser.add_argument("--json", action="store_true", help="Output state as JSON")

    # list scenarios
    subparsers.add_parser("list-scenarios", help="List available chaos scenarios")

    # mcp command
    subparsers.add_parser("mcp", help="Run in Model Context Protocol (MCP) stdio mode")

    return parser.parse_args()

async def async_main():
    args = parse_args()
    if args.command == "list-scenarios" or not args.command:
        print("\n=== Available CloudAgentSwarm Chaos Scenarios ===")
        for s_id, s in SCENARIO_CATALOG.items():
            print(f"  • {s_id:22} [{s.severity.value:5}] - {s.name}")
        print("\nRun with: cloud-swarm simulate --scenario <id>\n")
        return

    if args.command == "simulate":
        scen = get_scenario(args.scenario)
        if not scen:
            print(f"Error: Unknown scenario {args.scenario}")
            sys.exit(1)

        provider = MockCloudProvider()
        provider.set_scenario(args.scenario, {})
        coordinator = SwarmCoordinator(provider)

        incident = Incident(
            title=scen.name,
            description=scen.description,
            severity=scen.severity,
            affected_services=[scen.target_service],
        )

        state = await coordinator.execute_swarm_loop(incident)
        render_swarm_run(state, args.json)

    elif args.command == "mcp":
        from ..mcp_server.server import create_mcp_server
        server = create_mcp_server()
        sys.stderr.write("CloudAgentSwarm MCP Server ready on stdio.\n")
        sys.stderr.flush()
        await server.run_stdio()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
