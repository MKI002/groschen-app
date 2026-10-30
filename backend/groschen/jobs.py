"""Background jobs (bank sync, imports) with progress the web UI can poll."""

import threading
import traceback
import uuid
from dataclasses import dataclass, field

from . import i18n


@dataclass
class Job:
    id: str
    kind: str
    state: str = "running"  # running | waiting | done | error
    message: str = ""
    steps: list = field(default_factory=list)
    result: dict | None = None
    error: str | None = None

    def add_steps(self, *labels: str) -> None:
        self.steps = [{"label": label, "state": "pending"} for label in labels]

    def step(self, index: int, state: str = "running", label: str | None = None) -> None:
        for i, s in enumerate(self.steps):
            if i < index and s["state"] in ("pending", "running"):
                s["state"] = "done"
        if 0 <= index < len(self.steps):
            self.steps[index]["state"] = state
            if label:
                self.steps[index]["label"] = label

    def wait(self, message: str) -> None:
        self.state = "waiting"
        self.message = message

    def resume(self) -> None:
        self.state = "running"
        self.message = ""

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "state": self.state,
            # Stored in English, shown in the language of whoever asks.
            "message": i18n.tr(self.message),
            "steps": [{**s, "label": i18n.tr(s["label"])} for s in self.steps],
            "result": self.result,
            "error": i18n.tr(self.error),
        }


_jobs: dict[str, Job] = {}
_lock = threading.Lock()


def get(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def running(kind: str) -> Job | None:
    with _lock:
        for job in _jobs.values():
            if job.kind == kind and job.state in ("running", "waiting"):
                return job
    return None


def start(kind: str, fn, *args, **kwargs) -> Job:
    """Run ``fn(job, *args)`` in a thread. Errors end up in ``job.error`` as plain text."""
    job = Job(id=uuid.uuid4().hex[:12], kind=kind)
    with _lock:
        _jobs[job.id] = job
        if len(_jobs) > 50:
            for old in list(_jobs)[:-50]:
                _jobs.pop(old, None)

    def run():
        try:
            result = fn(job, *args, **kwargs)
            job.result = result if isinstance(result, dict) else job.result
            for s in job.steps:
                if s["state"] in ("pending", "running"):
                    s["state"] = "done"
            job.state = "done"
            job.message = ""
        except UserFacingError as exc:
            job.state = "error"
            job.error = str(exc)
            _fail_running_step(job)
        except Exception as exc:  # pragma: no cover - unexpected failures still reach the UI
            traceback.print_exc()
            job.state = "error"
            job.error = f"Something went wrong: {exc}"
            _fail_running_step(job)

    threading.Thread(target=run, name=f"job-{kind}", daemon=True).start()
    return job


def run_inline(kind: str, fn, *args, **kwargs) -> Job:
    """Run a job in the current thread (scheduler and tests)."""
    job = Job(id=uuid.uuid4().hex[:12], kind=kind)
    try:
        job.result = fn(job, *args, **kwargs)
        job.state = "done"
    except UserFacingError as exc:
        job.state = "error"
        job.error = str(exc)
    return job


def _fail_running_step(job: Job) -> None:
    for s in job.steps:
        if s["state"] == "running":
            s["state"] = "error"


class UserFacingError(Exception):
    """An error whose message is written for the person using the app."""
