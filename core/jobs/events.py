"""
Event system for the Job System.

Jobs emit an event whenever their status changes. The EventBus lets any
part of the application subscribe to these events (logging, future
notifications, dashboards...) without coupling to the Job or Worker
implementation.
"""

from dataclasses import dataclass
from typing import Callable, List


@dataclass
class JobEvent:
    job_id: str
    job_name: str
    from_status: str
    to_status: str
    message: str = ""


class EventBus:
    """A minimal publish/subscribe bus for job events."""

    def __init__(self) -> None:
        self._subscribers: List[Callable[[JobEvent], None]] = []

    def subscribe(self, handler: Callable[[JobEvent], None]) -> None:
        self._subscribers.append(handler)

    def publish(self, event: JobEvent) -> None:
        for handler in self._subscribers:
            handler(event)
