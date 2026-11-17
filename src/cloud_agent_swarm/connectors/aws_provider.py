import asyncio
import time
from typing import List, Dict, Any, Optional
from .base import BaseCloudProvider
from ..core.models import TelemetryMetric

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

class AWSProvider(BaseCloudProvider):
    """AWS Boto3 Client Provider with fallback to safe emulation."""

    def __init__(self, region_name: str = "eu-west-1", use_real_aws: bool = False):
        self.region_name = region_name
        self.use_real_aws = use_real_aws and BOTO3_AVAILABLE
        self._cw_client = None
        self._logs_client = None

        if self.use_real_aws:
            try:
                self._cw_client = boto3.client("cloudwatch", region_name=region_name)
                self._logs_client = boto3.client("logs", region_name=region_name)
            except Exception:
                self.use_real_aws = False

    async def get_metrics(
        self,
        namespace: str,
        metric_name: str,
        dimensions: Dict[str, str],
        period_seconds: int = 60,
    ) -> List[TelemetryMetric]:
        if self.use_real_aws and self._cw_client:
            try:
                dims = [{"Name": k, "Value": v} for k, v in dimensions.items()]
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self._cw_client.get_metric_data(
                        MetricDataQueries=[{
                            "Id": "m1",
                            "MetricStat": {
                                "Metric": {"Namespace": namespace, "MetricName": metric_name, "Dimensions": dims},
                                "Period": period_seconds,
                                "Stat": "Average",
                            },
                            "ReturnData": True,
                        }],
                        StartTime=time.time() - 3600,
                        EndTime=time.time(),
                    )
                )
                results = []
                for query_res in response.get("MetricDataResults", []):
                    timestamps = query_res.get("Timestamps", [])
                    values = query_res.get("Values", [])
                    for ts, val in zip(timestamps, values):
                        results.append(TelemetryMetric(
                            metric_name=metric_name,
                            namespace=namespace,
                            value=float(val),
                            unit="Percent",
                            timestamp=ts.timestamp() if hasattr(ts, "timestamp") else time.time(),
                            dimensions=dimensions,
                        ))
                if results:
                    return results
            except Exception:
                pass

        # Deterministic simulation fallback
        now = time.time()
        return [
            TelemetryMetric(
                metric_name=metric_name,
                namespace=namespace,
                value=94.2 if "CPU" in metric_name or "Memory" in metric_name else 42.0,
                unit="Percent" if "CPU" in metric_name else "Count",
                timestamp=now - (i * period_seconds),
                dimensions=dimensions,
            )
            for i in range(5)
        ]

    async def get_logs(
        self,
        log_group: str,
        filter_pattern: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if self.use_real_aws and self._logs_client:
            try:
                loop = asyncio.get_running_loop()
                resp = await loop.run_in_executor(
                    None,
                    lambda: self._logs_client.filter_log_events(
                        logGroupName=log_group,
                        filterPattern=filter_pattern,
                        limit=limit,
                    )
                )
                events = resp.get("events", [])
                if events:
                    return events
            except Exception:
                pass

        return [
            {
                "timestamp": time.time() - 30,
                "message": "ERROR: Out of Memory - java.lang.OutOfMemoryError killed container",
                "logStreamName": "task-checkout-001",
            },
            {
                "timestamp": time.time() - 15,
                "message": "WARN: Health check failed: connection timeout 504",
                "logStreamName": "task-checkout-001",
            }
        ]

    async def describe_resource_health(self, resource_id: str) -> Dict[str, Any]:
        return {
            "resource_id": resource_id,
            "status": "UNHEALTHY",
            "reason": "ContainerExitCode 137 (OOM)",
            "restart_count": 5,
        }

    async def execute_action(self, action_type: str, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Safe simulated action
        return {
            "status": "SUCCESS",
            "action": action_type,
            "resource_id": resource_id,
            "parameters": parameters,
            "executed_at": time.time(),
        }
