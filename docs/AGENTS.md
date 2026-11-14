# Swarm Agent Personas & Protocols

Every agent in `CloudAgentSwarm` encapsulates an autonomous SRE domain:

## 1. Incident Commander (`IncidentCommanderAgent`)
- **Responsibility:** War room leadership, initial SEV classification, quorum verification, and final resolution declaration.
- **Decision Engine:** Evaluates state progression through finite state checkpoints.

## 2. Telemetry Investigator (`TelemetryInvestigatorAgent`)
- **Responsibility:** Deep log correlation, Prometheus / CloudWatch metric spike detection, and root-cause hypothesis generation.
- **Key Output:** Identified `Anomaly` objects with confidence ratings (0.0 to 1.0).

## 3. Blast Radius Analyst (`BlastRadiusAnalystAgent`)
- **Responsibility:** Security boundary validation, IAM privilege analysis, VPC crossing risk, and Human-in-the-Loop gating.
- **Rule:** If Risk Score > 40.0 or IAM credential compromise is suspected, human approval is mandatory.

## 4. Remediation Planner (`RemediationPlannerAgent`)
- **Responsibility:** Generates atomic remediation actions (scale, restart, quarantine, route update) with deterministic rollback commands and estimated RTO.
