"""In-process event bus used to stream real-time agent activity to the GUI.

The bus is intentionally tiny and dependency free: agents, tools and API
handlers publish plain dictionaries, and the WebSocket layer fans them out to
every connected desktop client.

Event payload contract (see docs/ARCHITECTURE.md):
    {
      "type": "tool.completed",       # dotted event name
      "timestamp": "2026-01-01T00:00:00Z",
      "sequence": 12,
      "conversation_id": "default",
      ...                            # event specific fields
    }
"""

from __future__ import annotations

import asyncio
import threading
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional, Set

DEFAULT_QUEUE_SIZE = 256


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class EventBus:
    """Fan-out event bus with a bounded queue per subscriber."""

    def __init__(self, queue_size: int = DEFAULT_QUEUE_SIZE) -> None:
        self._subscribers: Set["asyncio.Queue[Dict[str, Any]]"] = set()
        self._lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._queue_size = queue_size
        self._sequence = 0
        self._history: List[Dict[str, Any]] = []
        self._history_limit = 100

    # -- publishing ---------------------------------------------------------

    def emit(self, event_type: str, *, loop: Optional[asyncio.AbstractEventLoop] = None, **payload: Any) -> None:
        """Publish an event. Safe to call from a worker thread."""
        try:
            running_loop = loop or asyncio.get_running_loop()
        except RuntimeError:
            running_loop = self._loop

        if running_loop is not None and running_loop.is_running() and not self._in_loop_thread(running_loop):
            running_loop.call_soon_threadsafe(self._publish_now, event_type, payload)
            return

        self._publish_now(event_type, payload)

    @staticmethod
    def _in_loop_thread(loop: asyncio.AbstractEventLoop) -> bool:
        try:
            running = asyncio.get_running_loop()
        except RuntimeError:
            return False
        return running is loop

    def _publish_now(self, event_type: str, payload: Dict[str, Any]) -> None:
        self._sequence += 1
        event: Dict[str, Any] = {
            "type": event_type,
            "timestamp": _utc_now(),
            "sequence": self._sequence,
            **payload,
        }
        self._history.append(event)
        if len(self._history) > self._history_limit:
            del self._history[: len(self._history) - self._history_limit]

        with self._lock:
            targets = list(self._subscribers)
        for queue in targets:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Slow consumer: drop the oldest event so the stream keeps moving.
                try:
                    queue.get_nowait()
                    queue.put_nowait(event)
                except Exception:  # pragma: no cover - defensive
                    pass

    # -- subscribing --------------------------------------------------------

    async def subscribe(self) -> AsyncIterator[Dict[str, Any]]:
        queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue(maxsize=self._queue_size)
        self._loop = asyncio.get_running_loop()
        with self._lock:
            self._subscribers.add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            with self._lock:
                self._subscribers.discard(queue)

    # -- introspection ------------------------------------------------------

    @property
    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subscribers)

    def recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._history[-limit:]

    def reset(self) -> None:
        with self._lock:
            self._subscribers.clear()
        self._history.clear()
        self._sequence = 0


# Event type constants (kept in one place so producers and the GUI agree).
class EventType:
    AGENT_STARTED = "agent.started"
    AGENT_THINKING = "agent.thinking"
    AGENT_PLANNED = "agent.planned"
    AGENT_COMPLETED = "agent.completed"
    AGENT_ERROR = "agent.error"
    AGENT_CANCELLED = "agent.cancelled"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    CONFIRMATION_REQUIRED = "confirmation.required"
    CONFIRMATION_RESOLVED = "confirmation.resolved"
    SYSTEM_STATUS = "system.status"
    VOICE_LISTENING = "voice.listening"
    VOICE_TRANSCRIBING = "voice.transcribing"
    VOICE_GENERATING = "voice.generating"
    VOICE_SPEAKING = "voice.speaking"
    VOICE_INTERRUPTED = "voice.interrupted"


event_bus = EventBus()

__all__ = ["EventBus", "EventType", "event_bus"]
