import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
import asyncio
from cloud_agent_swarm.core.models import (
    Incident, Severity, IncidentStatus, TelemetryMetric, Anomaly,
    BlastRadiusReport, RemediationAction, RemediationPlan, SwarmState
)
from cloud_agent_swarm.core.event_bus import EventBus
from cloud_agent_swarm.core.protocol import MessageEnvelope, ProtocolVerb
from cloud_agent_swarm.core.config import load_config

class TestCoreModels(unittest.TestCase):
    def test_incident_lifecycle(self):
        inc = Incident(
            title="Checkout Pod OOM Storm",
            description="Memory pressure triggering 502 bad gateway",
            severity=Severity.SEV2,
            affected_services=["checkout-api", "payment-service"],
        )
        self.assertEqual(inc.severity, Severity.SEV2)
        self.assertEqual(inc.status, IncidentStatus.DETECTED)
        d = inc.to_dict()
        self.assertEqual(d["severity"], "SEV-2")
        self.assertEqual(d["status"], "DETECTED")

    def test_blast_radius_and_remediation(self):
        blast = BlastRadiusReport(
            incident_id="inc-123",
            risk_score=75.5,
            affected_components=["checkout-pod", "rds-proxy"],
            requires_human_approval=True
        )
        self.assertTrue(blast.requires_human_approval)
        self.assertGreaterEqual(blast.risk_score, 50.0)

        action = RemediationAction(
            action_type="scale_deployment",
            target_resource="checkout-api",
            parameters={"replicas": 5},
            risk_level="LOW"
        )
        plan = RemediationPlan(
            incident_id="inc-123",
            actions=[action],
            total_risk_score=20.0
        )
        self.assertEqual(len(plan.actions), 1)

class TestEventBus(unittest.IsolatedAsyncioTestCase):
    async def test_pub_sub_wildcard(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe("incident.*", handler)
        await bus.publish("incident.detected", {"incident_id": "inc-001"})
        await bus.publish("incident.resolved", {"incident_id": "inc-001"})
        await bus.publish("telemetry.metric", {"val": 42})

        self.assertEqual(len(received), 2)
        self.assertEqual(received[0].topic, "incident.detected")
        self.assertEqual(received[1].topic, "incident.resolved")

    async def test_dead_letter_handling(self):
        bus = EventBus()

        async def bad_handler(event):
            raise ValueError("Intentional subscriber crash")

        bus.subscribe("test.fail", bad_handler)
        await bus.publish("test.fail", {"data": 123})

        self.assertEqual(len(bus.dead_letters), 1)
        self.assertEqual(bus.dead_letters[0]["error"], "Intentional subscriber crash")

class TestProtocolAndConfig(unittest.TestCase):
    def test_message_envelope(self):
        env = MessageEnvelope(
            verb=ProtocolVerb.TRIAGE_REQUEST,
            sender_role="incident_commander",
            payload={"incident_id": "inc-test"}
        )
        self.assertTrue(env.validate())

    def test_config_loader(self):
        cfg = load_config()
        self.assertTrue(cfg.mock_mode)
        self.assertGreater(cfg.max_swarm_iterations, 0)

if __name__ == "__main__":
    unittest.main()
