"""
Job System demonstration for AI Video Studio.

Creates a single fictional job, pushes it through a JobQueue and a Worker,
and prints every state transition (PENDING -> RUNNING -> COMPLETED). No AI
model is involved: the job's task is a plain simulated function.
"""

import time

from jobs import EventBus, Job, JobQueue, Worker


def log_transition(event) -> None:
    print(
        f"  [{event.job_id}] {event.job_name}: "
        f"{event.from_status} -> {event.to_status} ({event.message})"
    )


def fake_render_task(job: Job) -> str:
    """Simulated unit of work - stands in for a future real render/generation task."""
    print(f"  Running task for job {job.id} with payload: {job.payload}")
    time.sleep(0.2)
    return "demo-video.mp4 (simulated render)"


def main() -> None:
    print("=" * 60)
    print("AI VIDEO STUDIO - JOB SYSTEM DEMO")
    print("=" * 60)

    event_bus = EventBus()
    event_bus.subscribe(log_transition)

    job = Job(
        name="Render Demo Video",
        task=fake_render_task,
        payload={"scene_schema": "workflow/scene_schema.json"},
        event_bus=event_bus,
    )
    print(f"\nJob created: {job}")

    queue = JobQueue()
    queue.enqueue(job)
    print(f"Job enqueued. Queue size: {len(queue)}")

    worker = Worker(name="worker-1", queue=queue)
    print(f"\nWorker '{worker.name}' starting...\n")
    worker.run_all()

    print(f"\nFinal job state: {job}")
    print(f"Result: {job.result}")

    print("\nFull history:")
    for transition in job.history:
        print(f"  {transition.timestamp}  {transition.status.value}")


if __name__ == "__main__":
    main()
