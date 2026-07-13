"""
Job representation for the AI Video Studio Job System.

A Job wraps a unit of work (e.g. "render a video", "generate a storyboard")
together with its status, its full history of state transitions, and the
callable that performs the actual work. The task callable is injected, so
this class has no knowledge of what it actually runs - future workers can
plug in real render/generation tasks without changing this file.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .events import EventBus, JobEvent
from .status import JobStatus


@dataclass
class JobTransition:
    status: JobStatus
    timestamp: str


class Job:
    def __init__(
        self,
        name: str,
        task: Callable[["Job"], Any],
        payload: Optional[Dict[str, Any]] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.task = task
        self.payload = payload or {}
        self.result: Any = None
        self.error: Optional[str] = None
        self.event_bus = event_bus

        self.status = JobStatus.PENDING
        self.history: List[JobTransition] = []
        self._record_transition(JobStatus.PENDING)

    def _record_transition(self, status: JobStatus) -> None:
        self.history.append(
            JobTransition(
                status=status,
                timestamp=datetime.now().isoformat(timespec="seconds"),
            )
        )

    def set_status(self, status: JobStatus, message: str = "") -> None:
        previous = self.status
        self.status = status
        self._record_transition(status)

        if self.event_bus:
            self.event_bus.publish(
                JobEvent(
                    job_id=self.id,
                    job_name=self.name,
                    from_status=previous.value,
                    to_status=status.value,
                    message=message,
                )
            )

    def run(self) -> None:
        """Execute the job's task, moving PENDING -> RUNNING -> COMPLETED/FAILED."""
        self.set_status(JobStatus.RUNNING, "Job started.")
        try:
            self.result = self.task(self)
            self.set_status(JobStatus.COMPLETED, "Job finished successfully.")
        except Exception as exc:  # a failing task must not crash the worker
            self.error = str(exc)
            self.set_status(JobStatus.FAILED, f"Job failed: {self.error}")

    def __repr__(self) -> str:
        return f"Job(id={self.id}, name={self.name!r}, status={self.status.value})"
