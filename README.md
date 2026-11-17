<h1 align="center">⚡ CloudAgentSwarm</h1>
<p align="center">
  <b>Autonomous Multi-Agent Cloud SRE &amp; Incident Commander for AWS &amp; Kubernetes</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Protocol-Model_Context_Protocol_(MCP)-8A2BE2?style=flat-square" alt="MCP" />
  <img src="https://img.shields.io/badge/AWS-Well--Architected-FF9900?style=flat-square&logo=amazon-aws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/Kubernetes-Production--Ready-326CE5?style=flat-square&logo=kubernetes&logoColor=white" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/Security-Zero--Trust_Guardrails-green?style=flat-square" alt="Security" />
</p>

---

## 🎯 Overview

**CloudAgentSwarm** is an enterprise-grade autonomous multi-agent platform engineered to triage, investigate, contain, and remediate cloud infrastructure outages in seconds.

Instead of relying on a monolithic prompt or single LLM script, `CloudAgentSwarm` deploys **specialized SRE agents** that collaborate over an asynchronous event bus, formulate root-cause hypotheses, enforce strict **Blast-Radius Guardrails**, and generate comprehensive post-mortem documentation.

```
                    ┌───────────────────────────────┐
                    │  CloudWatch / Prometheus Alert │
                    └───────────────┬───────────────┘
                                    │ (Event: incident.detected)
                                    ▼
                    ┌───────────────────────────────┐
                    │      Incident Commander       │
                    │  (Triage, SEV score, Quorum)  │
                    └───────┬───────────────┬───────┘
                            │               │
            ┌───────────────┘               └───────────────┐
            ▼                                               ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│     Telemetry Investigator    │               │     Blast Radius Analyst      │
│ (Metrics, CloudTrail, Traces) │               │   (IAM, Network, Financial)   │
└───────────────┬───────────────┘               └───────────────┬───────────────┘
                │                                               │
                └───────────────┬───────────────────────────────┘
                                ▼
                ┌───────────────────────────────┐
                │      Remediation Planner      │
                │  (Playbooks, Rollback, RTO)   │
                └───────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │    Human-in-the-Loop Check    │ (If Risk > 40% or Destructive)
                └───────────────┬───────────────┘
                                │ (Approved)
                                ▼
                ┌───────────────────────────────┐
                │   Safe Remediation Executor   │
                └───────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │   Post-Mortem & Audit Trail   │
                └───────────────────────────────┘
```

---

## 🤖 The Swarm Agent Roster

| Agent Role | Persona | Key Responsibilities |
|---|---|---|
| **Incident Commander** | `Commander-Prime` | War room coordination, SEV-1 to SEV-4 classification, consensus quorum verification. |
| **Telemetry Investigator** | `Telemetry-Investigator-01` | CloudWatch Logs Insights, PromQL evaluation, metric spike correlation, root cause hypotheses. |
| **Blast Radius Analyst** | `Blast-Radius-Sentinel` | IAM privilege escalation detection, VPC boundary checks, financial impact calculation, HITL gating. |
| **Remediation Planner** | `Remediation-Architect` | Synthesizes surgical remediation actions (scale, restart, quarantine) with deterministic rollback commands. |

---

## 🛡️ Zero-Guess Safety & Guardrails

- **Immutable Forbidden Actions:** Commands such as `drop_database`, `delete_vpc`, or `destroy_kms_key` are hard-blocked at the AST level by `GuardrailEnforcer`.
- **Human-in-the-Loop (HITL):** Any remediation action carrying a risk score $> 40.0$ or flagged as `is_destructive` immediately pauses execution and requires interactive operator confirmation.
- **Rollback Guarantee:** Every generated action must declare an exact inverse rollback command before being dispatched.

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/ekrmcakir/cloud-agent-swarm.git
cd cloud-agent-swarm
pip install -e .
```

### 2. Run Built-In Chaos Simulations
```bash
# Simulate a Kubernetes OOMKilled cascade
cloud-swarm simulate --scenario oom_cascade

# Simulate a compromised IAM credential & S3 exfiltration
cloud-swarm simulate --scenario iam_key_leak

# List all available chaos scenarios
cloud-swarm list-scenarios
```

### 3. Model Context Protocol (MCP) Integration
Add `CloudAgentSwarm` to your Claude Code, Cursor, or Antigravity `mcpServers` configuration:

```json
{
  "mcpServers": {
    "cloud-agent-swarm": {
      "command": "python",
      "args": ["-m", "cloud_agent_swarm.cli.main", "mcp"]
    }
  }
}
```

---

## 🧪 Test Suite

Run the full end-to-end and unit test matrix:

```bash
make test
# or
python3 -m unittest discover -s tests -p "test_*.py"
```

```text
Ran 12 tests in 0.045s
OK
```

---

## 📦 Architecture & Directory Layout

```
cloud-agent-swarm/
├── src/cloud_agent_swarm/
│   ├── core/           # Domain models, async event-bus, protocols, config
│   ├── connectors/     # AWS, K8s, Prometheus, and high-fidelity Mock providers
│   ├── scenarios/      # Pre-configured chaos injection catalog
│   ├── agents/         # Commander, Investigator, Blast Radius, Remediation agents
│   ├── swarm/          # State graph, coordinator, guardrails, HITL, postmortem generator
│   ├── mcp_server/     # MCP 2.x standard JSON-RPC tools and stdio server
│   ├── cli/            # Rich interactive TUI cockpit and subcommands
│   ├── web/            # Lightweight real-time war room server
│   └── observability/  # OpenTelemetry decision latency exporter
├── chart/              # Production Kubernetes Helm chart
├── tests/              # 100% test coverage suite (unit + e2e)
├── Dockerfile          # Multi-stage zero-trust non-root container
└── README.md
```

---

## 📜 License

Licensed under the [Apache License, Version 2.0](LICENSE).
© 2026 Ekrem Cakir.
