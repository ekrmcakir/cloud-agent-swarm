from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from ..core.models import Incident, Severity

@dataclass
class ScenarioDefinition:
    id: str
    name: str
    description: str
    target_service: str
    severity: Severity
    metrics_to_trigger: List[str]
    root_cause_explanation: str
    recommended_remediations: List[str]
    is_destructive_action_needed: bool = False
    blast_radius_risk_score: float = 30.0

SCENARIO_CATALOG: Dict[str, ScenarioDefinition] = {
    "oom_cascade": ScenarioDefinition(
        id="oom_cascade",
        name="Kubernetes OOMKilled Cascading CrashLoop",
        description="Checkout service pods hit memory limit of 512Mi due to sudden cache leak, cascading 502/504 errors across microservices.",
        target_service="checkout-service",
        severity=Severity.SEV1,
        metrics_to_trigger=["container_memory_working_set_bytes", "http_5xx_rate"],
        root_cause_explanation="Memory leak in product recommendation cache causing pods to exceed 512Mi limit and crash in SIGKILL (137).",
        recommended_remediations=["scale_deployment", "increase_memory_limit", "restart_pod"],
        is_destructive_action_needed=False,
        blast_radius_risk_score=25.0,
    ),
    "dynamodb_throttling": ScenarioDefinition(
        id="dynamodb_throttling",
        name="DynamoDB Read Capacity Throttling Spike",
        description="Flash sale surge causes order-events DynamoDB table to exceed provisioned 500 RCU, inducing upstream API timeouts.",
        target_service="order-events-table",
        severity=Severity.SEV2,
        metrics_to_trigger=["ThrottledRequests", "SuccessfulRequestLatency"],
        root_cause_explanation="Table provisioned capacity under-dimensioned for flash sale burst. Hot partition on tenant-id key.",
        recommended_remediations=["enable_auto_scaling", "switch_to_on_demand", "enable_dax_cache"],
        is_destructive_action_needed=False,
        blast_radius_risk_score=35.0,
    ),
    "iam_key_leak": ScenarioDefinition(
        id="iam_key_leak",
        name="Privileged AWS IAM Key Compromise & S3 Exposure",
        description="Public GitHub commit exposed IAM access key with AdministratorAccess; anomalous S3 GetObject bursts detected from unknown IP.",
        target_service="s3-customer-vault",
        severity=Severity.SEV1,
        metrics_to_trigger=["S3_GetObject_Count", "CloudTrail_UnauthorizedAttempts"],
        root_cause_explanation="Leaked long-lived access key actively utilized by unauthorized actor to scrape customer archives.",
        recommended_remediations=["quarantine_iam_role", "revoke_active_sessions", "apply_s3_deny_policy"],
        is_destructive_action_needed=True,
        blast_radius_risk_score=85.0,
    ),
    "split_brain_partition": ScenarioDefinition(
        id="split_brain_partition",
        name="Cross-AZ Network Partition & Peering Route Drop",
        description="Blackhole in eu-west-1b Transit Gateway route table isolates payment gateway replicas from auth cluster.",
        target_service="payment-transit-gateway",
        severity=Severity.SEV2,
        metrics_to_trigger=["PacketLossRate", "TCP_Retransmission_Rate"],
        root_cause_explanation="Erroneous Terraform state drift deleted route entry 10.100.0.0/16 pointing to TGW attachment.",
        recommended_remediations=["restore_route_entry", "drain_az_traffic", "failover_to_az_1a"],
        is_destructive_action_needed=False,
        blast_radius_risk_score=60.0,
    ),
}

def get_scenario(scenario_id: str) -> Optional[ScenarioDefinition]:
    return SCENARIO_CATALOG.get(scenario_id)
