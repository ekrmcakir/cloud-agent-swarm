from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time
from ..core.models import AgentRole, AgentMessage, SwarmState

@dataclass
class AgentMemory:
    """Working memory keeping track of thoughts, observations, and decisions."""
    thoughts: List[str] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)

    def record_thought(self, thought: str):
        self.thoughts.append(f"[{time.strftime('%H:%M:%S')}] {thought}")

    def record_observation(self, obs: Dict[str, Any]):
        self.observations.append(obs)

    def record_decision(self, decision: Dict[str, Any]):
        self.decisions.append(decision)

class BaseAgent(ABC):
    """Abstract autonomous agent base class participating in swarm consensus."""

    def __init__(self, role: AgentRole, name: str, system_prompt: str):
        self.role = role
        self.name = name
        self.system_prompt = system_prompt
        self.memory = AgentMemory()

    @abstractmethod
    async def process_turn(self, state: SwarmState) -> AgentMessage:
        """Executes an autonomous cognitive loop turn and emits a protocol message."""
        pass

    def log(self, message: str):
        self.memory.record_thought(message)
