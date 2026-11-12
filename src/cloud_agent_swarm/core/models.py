from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import time
import uuid

class Severity(str, Enum):
    SEV1 = "SEV-1"  # Catastrophic: Total outage or core data corruption
    SEV2 = "SEV-2"  # Critical: Impaired customer experience, SLA breach imminent
    SEV3 = "SEV-3"  # Moderate: Non-critical subsystem degradation
    SEV4 = "SEV-4"  # Low: Minor informational or transient anomaly

class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGING = "TRIAGING"
    INVESTIGATING = "INVESTIGATING"
    BLAST_RADIUS_EVALUATED = "BLAST_RADIUS_EVALUATED"
    REMEDIATION_PROPOSED = "REMEDIATION_PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    MITIGATING = "MITIGATING"
    MITIGATED = "MITIGATED"
    RESOLVED = "RESOLVED"
    ABORTED = "ABORTED"

class AgentRole(str, Enum):
    INCIDENT_COMMANDER = "incident_commander"
    TELEMETRY_INVESTIGATOR = "telemetry_investigator"
    BLAST_RADIUS_ANALYST = "blast_radius_analyst"
    REMEDIATION_PLANNER = "remediation_planner"

@dataclass
class TelemetryMetric:
    metric_name: str
    namespace: str
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    dimensions: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Anomaly:
    id: str = field(default_factory=lambda: f"anom-{uuid.uuid4().hex[:8]}")
    metric_name: str = ""
    anomaly_score: float = 0.0  # 0.0 to 1.0
    deviation_sigma: float = 0.0
    description: str = ""
    root_cause_hypothesis: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BlastRadiusReport:
    id: str = field(default_factory=lambda: f"blast-{uuid.uuid4().hex[:8]}")
    incident_id: str = ""
    risk_score: float = 0.0  # 0.0 (safe) to 100.0 (catastrophic)
    affected_components: List[str] = field(default_factory=list)
    iam_roles_at_risk: List[str] = field(default_factory=list)
    vpc_boundaries_crossed: bool = False
    financial_exposure_usd: float = 0.0
    requires_human_approval: bool = False
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RemediationAction:
    id: str = field(default_factory=lambda: f"act-{uuid.uuid4().hex[:8]}")
    action_type: str = ""  # restart_pod, scale_deployment, rollback_version, quarantine_iam_role, update_route_table
    target_resource: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    estimated_rto_seconds: int = 30
    rollback_command: str = ""
    is_destructive: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RemediationPlan:
    id: str = field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:8]}")
    incident_id: str = ""
    actions: List[RemediationAction] = field(default_factory=list)
    total_risk_score: float = 0.0
    requires_human_approval: bool = False
    approved_by: Optional[str] = None
    execution_status: str = "PENDING"  # PENDING, EXECUTING, SUCCESS, FAILED, ROLLED_BACK

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AgentMessage:
    id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    sender: AgentRole = AgentRole.INCIDENT_COMMANDER
    recipient: str = "broadcast"  # or specific agent role
    verb: str = "INFO"
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    in_reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["sender"] = self.sender.value
        return res

@dataclass
class Incident:
    id: str = field(default_factory=lambda: f"inc-{uuid.uuid4().hex[:8]}")
    title: str = ""
    description: str = ""
    severity: Severity = Severity.SEV3
    status: IncidentStatus = IncidentStatus.DETECTED
    source: str = "cloudwatch_alarm"
    affected_services: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    root_cause: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["severity"] = self.severity.value
        res["status"] = self.status.value
        return res

@dataclass
class SwarmState:
    incident: Incident
    telemetry: List[TelemetryMetric] = field(default_factory=list)
    anomalies: List[Anomaly] = field(default_factory=list)
    blast_radius: Optional[BlastRadiusReport] = None
    remediation_plan: Optional[RemediationPlan] = None
    messages: List[AgentMessage] = field(default_factory=list)
    iteration_count: int = 0
    is_completed: bool = False
    postmortem_markdown: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident": self.incident.to_dict(),
            "telemetry_count": len(self.telemetry),
            "anomalies": [a.to_dict() for a in self.anomalies],
            "blast_radius": self.blast_radius.to_dict() if self.blast_radius else None,
            "remediation_plan": self.remediation_plan.to_dict() if self.remediation_plan else None,
            "messages_count": len(self.messages),
            "iteration_count": self.iteration_count,
            "is_completed": self.is_completed,
            "has_postmortem": self.postmortem_markdown is not None,
        }
