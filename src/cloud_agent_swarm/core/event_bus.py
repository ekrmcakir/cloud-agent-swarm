import asyncio
from dataclasses import dataclass, field
from typing import Callable, Coroutine, Dict, List, Any, Optional
from collections import deque
import time
import fnmatch
import uuid

@dataclass
class Event:
    topic: str
    payload: Dict[str, Any]
    trace_id: str = field(default_factory=lambda: f"trc-{uuid.uuid4().hex[:12]}")
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:8]}")

class EventBus:
    """High-performance Asynchronous Event Bus with deque ring-buffer memory optimization."""
    
    def __init__(self, max_history: int = 1000):
        self._subscribers: Dict[str, List[Callable[[Event], Coroutine[Any, Any, None]]]] = {}
        self._history: deque = deque(maxlen=max_history)
        self._max_history = max_history
        self._dead_letter_queue: deque = deque(maxlen=200)

    def subscribe(self, topic_pattern: str, handler: Callable[[Event], Coroutine[Any, Any, None]]):
        if topic_pattern not in self._subscribers:
            self._subscribers[topic_pattern] = []
        self._subscribers[topic_pattern].append(handler)

    def _matches_topic(self, pattern: str, topic: str) -> bool:
        return fnmatch.fnmatch(topic, pattern)

    async def publish(self, topic: str, payload: Dict[str, Any], trace_id: Optional[str] = None) -> Event:
        event = Event(topic=topic, payload=payload)
        if trace_id:
            event.trace_id = trace_id
            
        self._history.append(event)

        tasks = []
        for pattern, handlers in self._subscribers.items():
            if self._matches_topic(pattern, topic):
                for handler in handlers:
                    tasks.append(self._safe_invoke(handler, event))

        if tasks:
            await asyncio.gather(*tasks)
        return event

    async def _safe_invoke(self, handler, event: Event):
        try:
            await handler(event)
        except Exception as e:
            self._dead_letter_queue.append({
                "event": event,
                "error": str(e),
                "timestamp": time.time(),
            })

    @property
    def history(self) -> List[Event]:
        return list(self._history)

    @property
    def dead_letters(self) -> List[Dict[str, Any]]:
        return list(self._dead_letter_queue)

    def clear(self):
        self._subscribers.clear()
        self._history.clear()
        self._dead_letter_queue.clear()
