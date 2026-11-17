# Demo Walkthrough: Autonomous Incident Resolution

### Scenario: `oom_cascade` (Checkout Service CrashLoop)

1. **Trigger:** `container_memory_working_set_bytes` exceeds 512Mi. Container exits with code `137`.
2. **Commander Triage:** Classifies incident as `SEV-1`. Broadcasts `TRIAGE_RESPONSE`.
3. **Parallel Investigation:**
   - `Telemetry Investigator` identifies `Heap exhaustion in microservice cache layer` (Confidence: 96%).
   - `Blast Radius Analyst` estimates blast radius at `35.0/100.0` (Contained to Kubernetes deployment).
4. **Remediation Plan:**
   - Action 1: `scale_deployment` (`replicas=4`)
   - Action 2: `restart_pod` (`grace_period=10`)
5. **Execution:** Actions safely applied. Health checks return 200 OK.
6. **Post-Mortem:** Generated in GitHub-flavored Markdown in `< 1.2s`.
