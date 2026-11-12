import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SwarmConfig:
    # Model config
    llm_model: str = "bedrock/anthropic.claude-3-5-sonnet"
    mock_mode: bool = True
    
    # Cloud Config
    aws_region: str = "eu-west-1"
    k8s_namespace: str = "production"
    
    # Swarm Limits
    max_swarm_iterations: int = 10
    consensus_quorum_ratio: float = 0.75
    hitl_risk_threshold: float = 40.0  # Actions with risk > 40 require human approval
    auto_remediation_enabled: bool = True
    
    # Observability
    otel_endpoint: Optional[str] = None
    log_level: str = "INFO"

def load_config() -> SwarmConfig:
    return SwarmConfig(
        llm_model=os.getenv("SWARM_LLM_MODEL", "bedrock/anthropic.claude-3-5-sonnet"),
        mock_mode=os.getenv("SWARM_MOCK_MODE", "true").lower() in ("true", "1", "yes"),
        aws_region=os.getenv("AWS_DEFAULT_REGION", "eu-west-1"),
        k8s_namespace=os.getenv("K8S_NAMESPACE", "production"),
        max_swarm_iterations=int(os.getenv("SWARM_MAX_ITERATIONS", "10")),
        hitl_risk_threshold=float(os.getenv("SWARM_HITL_THRESHOLD", "40.0")),
        auto_remediation_enabled=os.getenv("SWARM_AUTO_REMEDIATION", "true").lower() in ("true", "1", "yes"),
    )
