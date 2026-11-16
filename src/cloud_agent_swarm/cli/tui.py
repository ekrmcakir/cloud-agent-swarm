import json
import time
from typing import Dict, Any
from ..core.models import SwarmState

def render_swarm_run(state: SwarmState, output_json: bool = False):
    """Renders a beautiful war room visual dashboard in the terminal."""
    if output_json:
        print(json.dumps(state.to_dict(), indent=2))
        return

    inc = state.incident
    blast = state.blast_radius
    plan = state.remediation_plan

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"\n{BOLD}{CYAN}╔════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║                 CLOUD AGENT SWARM — SRE WAR ROOM COCKPIT                   ║{RESET}")
    print(f"{BOLD}{CYAN}╚════════════════════════════════════════════════════════════════════════════╝{RESET}\n")

    sev_color = RED if inc.severity.value in ("SEV-1", "SEV-2") else YELLOW
    print(f" {BOLD}Incident:{RESET}   {inc.title}")
    print(f" {BOLD}Severity:{RESET}   {sev_color}{inc.severity.value}{RESET} | Status: {GREEN}{inc.status.value}{RESET}")
    print(f" {BOLD}Root Cause:{RESET} {YELLOW}{inc.root_cause or 'Investigating'}{RESET}\n")

    print(f"{BOLD}--- 🤖 Agent Swarm Dialogue Log ---{RESET}")
    for msg in state.messages:
        role_tag = f"[{msg.sender.value:22}]"
        print(f"  {CYAN}{role_tag}{RESET} -> {BOLD}{msg.verb:24}{RESET} to: {msg.recipient}")

    if blast:
        print(f"\n{BOLD}--- 🛡️  Blast Radius & Security Perimeter ---{RESET}")
        risk_color = RED if blast.risk_score > 60 else (YELLOW if blast.risk_score > 30 else GREEN)
        print(f"  Risk Score:            {risk_color}{blast.risk_score:.1f} / 100.0{RESET}")
        print(f"  VPC Crossed:           {'Yes (CRITICAL)' if blast.vpc_boundaries_crossed else 'No (Contained)'}")
        print(f"  Human Approval Gated:  {'YES' if blast.requires_human_approval else 'NO'}")
        print(f"  Financial Exposure:    ${blast.financial_exposure_usd:,.2f}")

    if plan:
        print(f"\n{BOLD}--- ⚡ Remediation Actions Executed ---{RESET}")
        for idx, act in enumerate(plan.actions, 1):
            print(f"  {idx}. [{GREEN}{act.action_type}{RESET}] on {act.target_resource}")
            print(f"     Risk: {act.risk_level} | Est. RTO: {act.estimated_rto_seconds}s | Rollback: {act.rollback_command}")

    print(f"\n{GREEN}✔ Incident resolved and post-mortem generated successfully!{RESET}\n")
