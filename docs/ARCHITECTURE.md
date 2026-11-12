# CloudAgentSwarm Architecture

`CloudAgentSwarm` is an autonomous, multi-agent SRE and incident resolution platform designed for enterprise AWS and Kubernetes infrastructure.

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

## Core Tenets
1. **Zero-Guess Safety:** No destructive action (e.g. restart pod, scale deployment, alter IAM) executes without blast-radius scoring and human approval if the score exceeds the safety budget.
2. **Distributed Consensus:** All agents must reach quorum (75% agreement) on root cause hypothesis before remediation planning begins.
3. **Traceability:** Every agent dialogue, telemetry metric query, and command executed is signed with a deterministic trace ID.
