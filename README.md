<h1 align="center">⚡ CloudAgentSwarm</h1>

<p align="center">
  <b>Autonomous Multi-Agent Cloud SRE &amp; Incident Commander for AWS &amp; Kubernetes</b>
</p>

<p align="center">
  <a href="https://github.com/ekrmcakir/cloud-agent-swarm/actions/workflows/ci.yml">
    <img src="https://github.com/ekrmcakir/cloud-agent-swarm/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  </a>
  <a href="https://github.com/ekrmcakir/cloud-agent-swarm/releases/tag/v1.0.0">
    <img src="https://img.shields.io/badge/Release-v1.0.0-blue.svg" alt="Release" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Protocol-MCP-8A2BE2" alt="MCP" />
  <img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License" />
</p>

---

## 🎯 What is CloudAgentSwarm?

**CloudAgentSwarm** is an autonomous incident response platform where specialized AI agents collaborate to triage, investigate, contain, and remediate cloud infrastructure outages.

Instead of a single monolithic prompt, tasks are distributed across role-specific agents that analyze telemetry, evaluate blast radius, enforce safety guardrails, and execute remediation with rollback guarantees.

```
 [Alert] ──► [Incident Commander] ──► [Telemetry Investigator]
                                               │ (Root Cause)
                                               ▼
 [Safe Execution] ◄── [Guardrails & HITL] ◄── [Blast Radius Analyst]
        │                                      │
        ▼                                      ▼
 [Post-Mortem] ◄────────────────────── [Remediation Planner]
```

---

## 🤖 Specialized Agents

| Agent | Role | Focus |
|---|---|---|
| **Incident Commander** | War Room Lead | Severity classification (SEV-1 to SEV-4) and consensus orchestration. |
| **Telemetry Investigator** | Observability | Correlates CloudWatch metrics, PromQL queries, and pod logs to find root causes. |
| **Blast Radius Analyst** | Safety & Security | Evaluates IAM privilege risks, VPC boundaries, and financial exposure. |
| **Remediation Planner** | Site Reliability | Generates atomic remediation actions with deterministic rollback commands. |

---

## 🛡️ Safety & Guardrails

- **Hard Guardrails:** Destructive operations (`drop_database`, `delete_vpc`, `destroy_kms_key`) are blocked at policy level.
- **Human-in-the-Loop (HITL):** Actions with risk score $> 40.0$ or flagged as destructive mandate interactive human approval.
- **Rollback Guarantee:** Every action requires a verified inverse rollback command before execution.

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/ekrmcakir/cloud-agent-swarm.git
cd cloud-agent-swarm
pip install -e .
```

### 2. Run Chaos Simulations

```bash
# List available scenarios
cloud-swarm list-scenarios

# Run Kubernetes OOM cascade simulation
cloud-swarm simulate --scenario oom_cascade

# Run with JSON output
cloud-swarm simulate --scenario iam_key_leak --json
```

---

## 🔌 Model Context Protocol (MCP)

CloudAgentSwarm runs as a native MCP stdio server, allowing Claude Desktop, Cursor, or Antigravity to trigger investigations:

```json
{
  "mcpServers": {
    "cloud-agent-swarm": {
      "command": "cloud-swarm",
      "args": ["mcp"]
    }
  }
}
```

**Exposed Tools:**
- `list_scenarios` — Lists runnable chaos outage scenarios.
- `trigger_investigation` — Runs the swarm against an incident.
- `get_postmortem` — Fetches the generated SRE post-mortem report.

---

## 🔥 Included Chaos Scenarios

1. `oom_cascade` (SEV-1): Kubernetes pod memory exhaustion (Exit code 137) triggering 502/504 errors.
2. `iam_key_leak` (SEV-1): Leaked administrator IAM key with unauthorized S3 data scraping.
3. `dynamodb_throttling` (SEV-2): Capacity burst exceeding provisioned RCU on hot partition.
4. `split_brain_partition` (SEV-2): Transit Gateway route drop causing cross-AZ communication failure.

---

## 🧪 Testing

```bash
make test
# or
python3 -m unittest discover -s tests -p "test_*.py"
```

---

## 📜 License

[Apache 2.0](LICENSE) © 2026 Ekrem Cakir.
