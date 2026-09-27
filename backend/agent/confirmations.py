"""Pending confirmation store for gated tool calls.

When the permission layer returns CONFIRM or ADMIN, the agent stores the exact
call here and asks the user. Only the stored arguments can later be executed,
so a confirmation can never be repurposed for a different command.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from config.settings import settings


@dataclass
class PendingAction:
    id: str
    tool: str
    arguments: Dict[str, Any]
    permission_level: str
    reason: str
    conversation_id: str = "default"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConfirmationStore:
    """In-memory, TTL bounded store of actions awaiting user approval."""

    def __init__(self, ttl_seconds: Optional[int] = None) -> None:
        self._ttl = ttl_seconds if ttl_seconds is not None else settings.confirmation_ttl_seconds
        self._actions: Dict[str, PendingAction] = {}
        self._lock = threading.Lock()

    def create(
        self,
        tool: str,
        arguments: Dict[str, Any],
        permission_level: str,
        reason: str,
        conversation_id: str = "default",
    ) -> PendingAction:
        self.purge_expired()
        action = PendingAction(
            id=uuid.uuid4().hex,
            tool=tool,
            arguments=dict(arguments),
            permission_level=permission_level,
            reason=reason,
            conversation_id=conversation_id,
        )
        with self._lock:
            self._actions[action.id] = action
        return action

    def get(self, action_id: str) -> Optional[PendingAction]:
        with self._lock:
            action = self._actions.get(action_id)
        if action is None:
            return None
        if self._is_expired(action):
            self.discard(action_id)
            return None
        return action

    def resolve(self, action_id: str) -> Optional[PendingAction]:
        action = self.get(action_id)
        if action is not None:
            self.discard(action_id)
        return action

    def discard(self, action_id: str) -> None:
        with self._lock:
            self._actions.pop(action_id, None)

    def purge_expired(self) -> int:
        with self._lock:
            expired = [key for key, action in self._actions.items() if self._is_expired(action)]
            for key in expired:
                self._actions.pop(key, None)
        return len(expired)

    def list(self) -> List[PendingAction]:
        self.purge_expired()
        with self._lock:
            return list(self._actions.values())

    def clear(self) -> None:
        with self._lock:
            self._actions.clear()

    def _is_expired(self, action: PendingAction) -> bool:
        return (time.time() - action.created_at) > self._ttl


store = ConfirmationStore()


__all__ = ["PendingAction", "ConfirmationStore", "store"]
