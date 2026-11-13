from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.models import TelemetryMetric

class BaseCloudProvider(ABC):
    """Abstract base interface for cloud infrastructure providers."""

    @abstractmethod
    async def get_metrics(
        self,
        namespace: str,
        metric_name: str,
        dimensions: Dict[str, str],
        period_seconds: int = 60,
    ) -> List[TelemetryMetric]:
        pass

    @abstractmethod
    async def get_logs(
        self,
        log_group: str,
        filter_pattern: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def describe_resource_health(self, resource_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def execute_action(self, action_type: str, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        pass
