# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-11-17

### Added
- **Core Architecture:** Asynchronous event bus with ring-buffer memory optimization and wildcard pattern matching.
- **Multi-Agent Roster:** Specialized personas for Incident Commander, Telemetry Investigator, Blast Radius Analyst, and Remediation Planner.
- **Safety Perimeter:** Immutable guardrail enforcement and Human-in-the-Loop approval gating for destructive actions.
- **Cloud Connectors:** AWS (CloudWatch/CloudTrail), Kubernetes (Pods/Events), Prometheus (PromQL), and Mock Chaos provider.
- **Model Context Protocol:** Native MCP 2.x stdio JSON-RPC server with tool definitions for external LLMs.
- **Cockpit CLI:** Rich TUI dashboard with live incident feeds and interactive operator prompts.
- **Packaging:** Multi-stage zero-trust Dockerfile and Kubernetes Helm chart.
