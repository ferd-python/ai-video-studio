"""
A simple synchronous Worker that pulls jobs from a JobQueue and runs them
one after another. Future workers (parallel, async, remote) can reuse the
same Job / JobQueue / EventBus building blocks without changing this
interface.
"""

from .queue import JobQueue


class Worker:
    def __init__(self, name: str, queue: JobQueue) -> None:
        self.name = name
        self.queue = queue

    def run_all(self) -> None:
        """Process every job currently in the queue, in FIFO order."""
        while not self.queue.is_empty():
            job = self.queue.dequeue()
            if job is None:
                break
            job.run()
