from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid

class ProtocolVerb(str, Enum):
    ALERT_TRIGGERED = "ALERT_TRIGGERED"
    TRIAGE_REQUEST = "TRIAGE_REQUEST"
    TRIAGE_RESPONSE = "TRIAGE_RESPONSE"
    INVESTIGATE_REQUEST = "INVESTIGATE_REQUEST"
    TELEMETRY_ANOMALY_FOUND = "TELEMETRY_ANOMALY_FOUND"
    BLAST_RADIUS_REQUEST = "BLAST_RADIUS_REQUEST"
    BLAST_RADIUS_EVALUATED = "BLAST_RADIUS_EVALUATED"
    PROPOSE_REMEDIATION = "PROPOSE_REMEDIATION"
    CONSENSUS_VOTE = "CONSENSUS_VOTE"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    APPROVAL_VERDICT = "APPROVAL_VERDICT"
    EXECUTE_REMEDIATION = "EXECUTE_REMEDIATION"
    INCIDENT_RESOLVED = "INCIDENT_RESOLVED"
    POST_MORTEM_READY = "POST_MORTEM_READY"

@dataclass
class MessageEnvelope:
    verb: ProtocolVerb
    sender_role: str
    recipient: str = "broadcast"
    trace_id: str = field(default_factory=lambda: f"trc-{uuid.uuid4().hex[:12]}")
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: f"env-{uuid.uuid4().hex[:8]}")

    def validate(self) -> bool:
        if not self.sender_role:
            return False
        if not self.verb:
            return False
        return True
