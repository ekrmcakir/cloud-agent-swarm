import time
from typing import List
from .base import BaseAgent
from ..core.models import (
    AgentRole, AgentMessage, SwarmState, RemediationPlan, RemediationAction
)

class RemediationPlannerAgent(BaseAgent):
    """Synthesizes actionable, minimal-blast-radius remediation plans with rollbacks."""

    def __init__(self):
        super().__init__(
            role=AgentRole.REMEDIATION_PLANNER,
            name="Remediation-Architect",
            system_prompt=(
                "You are an SRE Remediation Planner. Propose atomic, idempotent remediation actions "
                "with clear rollback procedures and realistic RTO estimations."
            ),
        )

    async def process_turn(self, state: SwarmState) -> AgentMessage:
        self.log(f"Synthesizing remediation plan for incident {state.incident.id}")

        hypothesis = state.incident.root_cause or ""
        actions: List[RemediationAction] = []
        requires_hitl = False

        if state.blast_radius and state.blast_radius.requires_human_approval:
            requires_hitl = True

        if any(k in hypothesis for k in ("Heap", "OOMKilled", "137", "Memory", "OOM", "exhaustion")):
            actions = [
                RemediationAction(
                    action_type="scale_deployment",
                    target_resource="checkout-service-deployment",
                    parameters={"replicas": 4},
                    risk_level="LOW",
                    estimated_rto_seconds=25,
                    rollback_command="kubectl scale deployment checkout-service-deployment --replicas=2",
                    is_destructive=False,
                ),
                RemediationAction(
                    action_type="restart_pod",
                    target_resource="checkout-service-pod-crashloop",
                    parameters={"grace_period": 10},
                    risk_level="LOW",
                    estimated_rto_seconds=15,
                    rollback_command="kubectl rollout undo deployment checkout-service-deployment",
                    is_destructive=False,
                ),
            ]
        elif "DynamoDB" in hypothesis or "Throttling" in hypothesis:
            actions = [
                RemediationAction(
                    action_type="update_dynamodb_capacity",
                    target_resource="order-events-table",
                    parameters={"billing_mode": "PAY_PER_REQUEST"},
                    risk_level="MEDIUM",
                    estimated_rto_seconds=45,
                    rollback_command="aws dynamodb update-table --billing-mode PROVISIONED",
                    is_destructive=False,
                )
            ]
        elif "Compromised" in hypothesis or "IAM" in hypothesis:
            actions = [
                RemediationAction(
                    action_type="quarantine_iam_role",
                    target_resource="arn:aws:iam::123456789012:user/leaked-dev-user",
                    parameters={"status": "Inactive", "attach_deny_policy": True},
                    risk_level="HIGH",
                    estimated_rto_seconds=5,
                    rollback_command="aws iam update-access-key --status Active",
                    is_destructive=True,
                ),
                RemediationAction(
                    action_type="apply_s3_deny_policy",
                    target_resource="arn:aws:s3:::prod-customer-vault",
                    parameters={"block_public_access": True},
                    risk_level="MEDIUM",
                    estimated_rto_seconds=10,
                    rollback_command="aws s3api put-public-access-block --public-access-block-configuration BlockPublicAcls=false",
                    is_destructive=False,
                )
            ]
            requires_hitl = True

        plan = RemediationPlan(
            incident_id=state.incident.id,
            actions=actions,
            total_risk_score=state.blast_radius.risk_score if state.blast_radius else 25.0,
            requires_human_approval=requires_hitl,
        )

        state.remediation_plan = plan
        self.memory.record_decision(plan.to_dict())

        return AgentMessage(
            sender=self.role,
            recipient=AgentRole.INCIDENT_COMMANDER.value,
            verb="PROPOSE_REMEDIATION",
            payload=plan.to_dict(),
        )
