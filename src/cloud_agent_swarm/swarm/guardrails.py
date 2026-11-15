from typing import List, Set
from ..core.models import RemediationAction

class GuardrailViolation(Exception):
    """Raised when an agent proposes an action that violates safety policy."""
    pass

class GuardrailEnforcer:
    """Hard guardrails preventing destructive or unconstrained infrastructure mutations."""

    FORBIDDEN_ACTIONS: Set[str] = {
        "drop_database",
        "delete_vpc",
        "purge_s3_bucket",
        "destroy_kms_key",
        "detach_all_internet_gateways",
    }

    def __init__(self, max_replicas_limit: int = 50):
        self.max_replicas_limit = max_replicas_limit

    def verify_action(self, action: RemediationAction):
        if action.action_type in self.FORBIDDEN_ACTIONS:
            raise GuardrailViolation(
                f"Action '{action.action_type}' is permanently prohibited by organization security policy."
            )

        if action.action_type == "scale_deployment":
            replicas = action.parameters.get("replicas", 1)
            if replicas > self.max_replicas_limit:
                raise GuardrailViolation(
                    f"Requested replica count {replicas} exceeds safe maximum threshold of {self.max_replicas_limit}."
                )

        if action.is_destructive and action.risk_level != "HIGH":
            raise GuardrailViolation(
                f"Destructive action '{action.action_type}' must be marked with HIGH risk level."
            )
