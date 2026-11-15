import asyncio
from enum import Enum
from typing import Dict, Any, Callable, Coroutine, List, Optional
from ..core.models import SwarmState, IncidentStatus

class NodeStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SwarmGraph:
    """Declarative state graph controlling the multi-agent incident lifecycle."""

    def __init__(self):
        self.nodes: Dict[str, Callable[[SwarmState], Coroutine[Any, Any, SwarmState]]] = {}
        self.transitions: Dict[str, Dict[str, str]] = {}
        self.audit_log: List[str] = []

    def add_node(self, name: str, handler: Callable[[SwarmState], Coroutine[Any, Any, SwarmState]]):
        self.nodes[name] = handler

    def add_transition(self, from_node: str, condition: str, to_node: str):
        if from_node not in self.transitions:
            self.transitions[from_node] = {}
        self.transitions[from_node][condition] = to_node

    async def run(self, initial_state: SwarmState, start_node: str = "triage") -> SwarmState:
        current_node_name = start_node
        state = initial_state

        while current_node_name and current_node_name != "end":
            self.audit_log.append(f"Transition -> Node: {current_node_name}")
            handler = self.nodes.get(current_node_name)
            if not handler:
                raise ValueError(f"Unknown graph node: {current_node_name}")

            state = await handler(state)

            # Determine next node
            transitions = self.transitions.get(current_node_name, {})
            condition = "default"
            if state.incident.status == IncidentStatus.AWAITING_APPROVAL:
                condition = "needs_approval"
            elif state.incident.status == IncidentStatus.RESOLVED or state.incident.status == IncidentStatus.MITIGATED:
                condition = "resolved"
            elif state.incident.status == IncidentStatus.ABORTED:
                condition = "aborted"

            current_node_name = transitions.get(condition, transitions.get("default", "end"))

        return state
