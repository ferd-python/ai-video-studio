"""Simple FIFO job queue for the AI Video Studio Job System."""

from collections import deque
from typing import Deque, List, Optional

from .job import Job


class JobQueue:
    def __init__(self) -> None:
        self._queue: Deque[Job] = deque()

    def enqueue(self, job: Job) -> None:
        self._queue.append(job)

    def dequeue(self) -> Optional[Job]:
        if not self._queue:
            return None
        return self._queue.popleft()

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def list_jobs(self) -> List[Job]:
        return list(self._queue)

    def __len__(self) -> int:
        return len(self._queue)
