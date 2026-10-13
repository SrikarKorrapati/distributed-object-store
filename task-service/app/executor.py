"""Background task execution simulator."""
import threading
import time
import random
from datetime import datetime, timezone

_store: dict = {}  # injected at startup
_lock = threading.Lock()


def inject_store(store: dict):
    global _store
    _store = store


def _run_task(task_id: str):
    """Simulates an AI agent working through a task with realistic progress steps."""
    step_count = random.randint(6, 14)
    fail_at = random.randint(step_count, step_count + 4)  # occasionally fail
    will_fail = random.random() < 0.15  # 15% failure rate

    for step in range(1, step_count + 1):
        time.sleep(random.uniform(0.8, 2.2))

        with _lock:
            task = _store.get(task_id)
            if task is None or task["status"] != "running":
                return

            progress = min(int((step / step_count) * 100), 99)
            task["progress"] = progress

        if will_fail and step == max(1, step_count // 2):
            time.sleep(0.5)
            with _lock:
                task = _store.get(task_id)
                if task and task["status"] == "running":
                    task["status"] = "failed"
                    task["progress"] = progress
                    task["completed_at"] = datetime.now(timezone.utc).isoformat()
                    task["error"] = random.choice([
                        "Agent timed out after exceeding max retries",
                        "Tool call returned unexpected error: connection refused",
                        "Context window exceeded: task description too long",
                        "External API dependency unreachable",
                    ])
            return

    time.sleep(random.uniform(0.5, 1.0))
    with _lock:
        task = _store.get(task_id)
        if task and task["status"] == "running":
            task["status"] = "completed"
            task["progress"] = 100
            task["completed_at"] = datetime.now(timezone.utc).isoformat()


def start_task_execution(task_id: str):
    t = threading.Thread(target=_run_task, args=(task_id,), daemon=True)
    t.start()
