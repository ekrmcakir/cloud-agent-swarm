import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
from cloud_agent_swarm.connectors.aws_provider import AWSProvider
from cloud_agent_swarm.connectors.k8s_provider import K8sProvider
from cloud_agent_swarm.connectors.prometheus_provider import PrometheusProvider
from cloud_agent_swarm.connectors.mock_provider import MockCloudProvider
from cloud_agent_swarm.scenarios.catalog import SCENARIO_CATALOG, get_scenario

class TestConnectors(unittest.IsolatedAsyncioTestCase):
    async def test_aws_provider(self):
        provider = AWSProvider(region_name="eu-west-1")
        metrics = await provider.get_metrics("AWS/ECS", "CPUUtilization", {"ServiceName": "checkout"})
        self.assertGreater(len(metrics), 0)
        self.assertEqual(metrics[0].unit, "Percent")

        logs = await provider.get_logs("/aws/ecs/checkout", "ERROR")
        self.assertGreater(len(logs), 0)

    async def test_k8s_provider(self):
        k8s = K8sProvider(namespace="production")
        health = await k8s.describe_resource_health("pod-checkout-1")
        self.assertEqual(health["phase"], "CrashLoopBackOff")

        act = await k8s.execute_action("restart_pod", "pod-checkout-1", {"grace_period": 0})
        self.assertEqual(act["status"], "SUCCESS")

    async def test_prometheus_provider(self):
        prom = PrometheusProvider()
        res = await prom.query_instant("http_requests_total")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["metric"]["status"], "502")

    async def test_mock_provider_scenario(self):
        mock = MockCloudProvider()
        mock.set_scenario("OOMKilled_Cascade", {"pod-1": {"status": "CRASHED"}})
        metrics = await mock.get_metrics("k8s", "MemoryUsage", {"pod": "pod-1"})
        self.assertAlmostEqual(metrics[0].value, 98.4)

        logs = await mock.get_logs("app-log", "FATAL")
        self.assertIn("OutOfMemoryError", logs[0]["message"])

        res = await mock.execute_action("scale_deployment", "checkout-deployment", {"replicas": 5})
        self.assertEqual(res["status"], "APPLIED")
        self.assertEqual(len(mock.executed_actions), 1)

    async def test_all_catalog_scenarios_in_mock(self):
        mock = MockCloudProvider()
        for scenario_id in SCENARIO_CATALOG:
            mock.set_scenario(scenario_id, {})
            metrics = await mock.get_metrics("test", "test_metric", {})
            self.assertIsNotNone(metrics)

class TestScenarios(unittest.TestCase):
    def test_catalog_integrity(self):
        self.assertIn("oom_cascade", SCENARIO_CATALOG)
        self.assertIn("dynamodb_throttling", SCENARIO_CATALOG)
        self.assertIn("iam_key_leak", SCENARIO_CATALOG)

        scen = get_scenario("iam_key_leak")
        self.assertIsNotNone(scen)
        self.assertTrue(scen.is_destructive_action_needed)
        self.assertGreater(scen.blast_radius_risk_score, 80.0)

if __name__ == "__main__":
    unittest.main()
