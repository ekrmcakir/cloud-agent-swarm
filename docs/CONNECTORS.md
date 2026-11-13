# Cloud & Telemetry Connectors

The connector layer decouples agent reasoning from the underlying infrastructure providers.

## Supported Interfaces
- **AWSProvider:** Queries CloudWatch Metrics, CloudWatch Logs Insights, and CloudTrail audit streams.
- **K8sProvider:** Fetches Pod phase status, events, deployment replicas, and container logs.
- **PrometheusProvider:** Evaluates instant PromQL and range metrics for time-series anomaly detection.
- **MockCloudProvider:** High-fidelity simulation engine for offline testing and chaos validation.

## Scenario Catalog
| Scenario ID | Name | Severity | Primary Root Cause |
|---|---|---|---|
| `oom_cascade` | K8s OOMKilled Cascade | SEV-1 | Cache leak triggering container exit code 137 |
| `dynamodb_throttling` | DynamoDB Capacity Exceeded | SEV-2 | Hot partition under flash sale burst |
| `iam_key_leak` | Leaked IAM Admin Key | SEV-1 | Public credential compromise with S3 scraping |
| `split_brain_partition` | Transit Gateway Route Drop | SEV-2 | Dropped CIDR route table entry |
