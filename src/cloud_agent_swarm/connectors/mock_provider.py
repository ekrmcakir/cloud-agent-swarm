import time
import asyncio
from typing import List, Dict, Any
from .base import BaseCloudProvider
from ..core.models import TelemetryMetric

class MockCloudProvider(BaseCloudProvider):
    """High-fidelity Mock Cloud Provider capable of simulating active multi-cloud anomalies."""

    def __init__(self):
        self._scenario_state: Dict[str, Any] = {
            "current_scenario": None,
            "resources": {},
            "execution_log": [],
        }

    def set_scenario(self, scenario_name: str, initial_resources: Dict[str, Any]):
        self._scenario_state["current_scenario"] = scenario_name
        self._scenario_state["resources"] = initial_resources
        self._scenario_state["execution_log"].clear()

    async def get_metrics(
        self,
        namespace: str,
        metric_name: str,
        dimensions: Dict[str, str],
        period_seconds: int = 60,
    ) -> List[TelemetryMetric]:
        scenario = (self._scenario_state.get("current_scenario") or "").lower()
        val = 50.0
        if "oom" in scenario:
            val = 98.4 if "Memory" in metric_name else 75.0
        elif "dynamo" in scenario or "throttl" in scenario:
            val = 312.0 if "ThrottledRequests" in metric_name else 4.0
        elif "iam" in scenario or "leak" in scenario:
            val = 1420.0 if "S3_GetObject_Count" in metric_name else 1.0

        return [
            TelemetryMetric(
                metric_name=metric_name,
                namespace=namespace,
                value=val,
                unit="Count" if "Count" in metric_name or "Throttled" in metric_name else "Percent",
                timestamp=time.time(),
                dimensions=dimensions,
            )
        ]

    async def get_logs(
        self,
        log_group: str,
        filter_pattern: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        scenario = (self._scenario_state.get("current_scenario") or "").lower()
        if "oom" in scenario:
            return [
                {"timestamp": time.time() - 20, "message": "FATAL: OutOfMemoryError in worker thread pool (ContainerExitCode 137)"},
                {"timestamp": time.time() - 10, "message": "Container exited with code 137 (SIGKILL)"},
            ]
        elif "dynamo" in scenario or "throttl" in scenario:
            return [
                {"timestamp": time.time() - 15, "message": "ProvisionedThroughputExceededException: The level of configured provisioned throughput for the table was exceeded"},
                {"timestamp": time.time() - 5, "message": "504 Gateway Timeout upstream DynamoDB order-events"},
            ]
        elif "iam" in scenario or "leak" in scenario:
            return [
                {"timestamp": time.time() - 30, "message": "CloudTrail: PutBucketPolicy Action=s3:GetObject Principal=* Resource=arn:aws:s3:::prod-customer-pii"},
                {"timestamp": time.time() - 10, "message": "CloudTrail: Unauthorized GetObject burst from IP 198.51.100.42"},
            ]
        return [{"timestamp": time.time(), "message": "System operational"}]

    async def describe_resource_health(self, resource_id: str) -> Dict[str, Any]:
        return self._scenario_state["resources"].get(
            resource_id,
            {"status": "HEALTHY", "resource_id": resource_id}
        )

    async def execute_action(self, action_type: str, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "action": action_type,
            "resource": resource_id,
            "parameters": parameters,
            "timestamp": time.time(),
            "status": "APPLIED",
        }
        self._scenario_state["execution_log"].append(record)
        return record

    @property
    def executed_actions(self) -> List[Dict[str, Any]]:
        return list(self._scenario_state["execution_log"])
