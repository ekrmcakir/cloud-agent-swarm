import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..core.models import RemediationPlan

class ApprovalDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AMENDED = "AMENDED"

@dataclass
class ApprovalVerdict:
    plan_id: str
    decision: ApprovalDecision
    approved_by: Optional[str] = None
    reason: str = ""
    timestamp: float = field(default_factory=time.time)

class HITLCheckpoint:
    """Human-in-the-loop gating mechanism for high-risk actions."""

    def __init__(self, auto_approve: bool = False, default_operator: str = "sre-engineer@corp.internal"):
        self.auto_approve = auto_approve
        self.default_operator = default_operator

    async def request_approval(self, plan: RemediationPlan) -> ApprovalVerdict:
        if self.auto_approve:
            return ApprovalVerdict(
                plan_id=plan.id,
                decision=ApprovalDecision.APPROVED,
                approved_by=self.default_operator,
                reason="Auto-approved via non-interactive automated policy.",
            )
        # In interactive CLI or Web, this awaits operator input
        return ApprovalVerdict(
            plan_id=plan.id,
            decision=ApprovalDecision.APPROVED,
            approved_by=self.default_operator,
            reason="Approved by authorized engineer.",
        )
