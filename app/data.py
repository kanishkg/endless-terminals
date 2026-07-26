"""Data access layer.

Reads tasks, runs, and trials directly from the filesystem. Results are cached
in memory after the first scan; the cache can be invalidated by touching any
file under the data roots (we re-scan based on directory mtime).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import tomllib  # py3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "harbor_tasks"
RUNS_ROOTS: list[Path] = [REPO_ROOT / "solution_sonnet"]


# ---------- task models ---------------------------------------------------- #


@dataclass
class TaskMeta:
    task_id: str  # e.g. "task_000000_021e3bf6"
    path: Path
    instruction: str
    description: str
    truth: str
    difficulty: str | None
    category: str | None
    tags: list[str]
    agent_timeout_sec: float | None
    verifier_timeout_sec: float | None
    cpus: int | None
    memory_mb: int | None
    storage_mb: int | None
    has_initial_test: bool
    has_final_test: bool
    has_solve_script: bool
    dockerfile_lines: int


# ---------- run/trial models ----------------------------------------------- #


@dataclass
class TrialSummary:
    run_id: str
    trial_id: str  # e.g. "task_000000_021e3bf6__BoihRjY"
    task_id: str
    reward: float | None
    exception: str | None
    exception_message: str | None
    exception_traceback: str | None
    n_episodes: int | None
    duration_sec: float | None
    n_input_tokens: int | None
    n_output_tokens: int | None
    n_cache_tokens: int | None
    cost_usd: float | None
    model_name: str | None
    started_at: str | None
    finished_at: str | None
    path: Path


@dataclass
class RunSummary:
    run_id: str
    root: Path
    started_at: str | None
    finished_at: str | None
    n_total_trials: int
    n_errors: int
    mean_reward: float | None
    model_name: str | None
    agent_import_path: str | None
    dataset_paths: list[str]
    n_attempts: int
    trials: list[TrialSummary] = field(default_factory=list)
    exception_breakdown: dict[str, int] = field(default_factory=dict)

    @property
    def pretty_model(self) -> str:
        return _pretty_model(self.model_name)

    @property
    def total_input_tokens(self) -> int:
        return sum((t.n_input_tokens or 0) for t in self.trials)

    @property
    def total_output_tokens(self) -> int:
        return sum((t.n_output_tokens or 0) for t in self.trials)

    @property
    def n_pass(self) -> int:
        return sum(1 for t in self.trials if (t.reward or 0) >= 1.0)

    @property
    def n_fail(self) -> int:
        return sum(1 for t in self.trials if t.reward == 0.0)

    @property
    def n_error_trials(self) -> int:
        return sum(1 for t in self.trials if t.exception)


# ---------- helpers -------------------------------------------------------- #


def _pretty_model(name: str | None) -> str:
    if not name:
        return "unknown"
    n = name.replace("anthropic--", "").replace("anthropic/", "")
    return n


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def _parse_iso_duration(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    from datetime import datetime

    def _p(s: str) -> datetime:
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)

    try:
        return (_p(end) - _p(start)).total_seconds()
    except Exception:
        return None


# ---------- task scanning -------------------------------------------------- #


def _scan_task(task_dir: Path) -> TaskMeta | None:
    if not task_dir.is_dir():
        return None
    task_json = _read_json(task_dir / "environment" / "task.json") or {}
    instruction = _read_text(task_dir / "instruction.md")
    toml_path = task_dir / "task.toml"
    toml_data: dict[str, Any] = {}
    if toml_path.exists():
        try:
            toml_data = tomllib.loads(toml_path.read_text())
        except Exception:
            toml_data = {}

    meta = toml_data.get("metadata", {}) or {}
    agent = toml_data.get("agent", {}) or {}
    verifier = toml_data.get("verifier", {}) or {}
    env = toml_data.get("environment", {}) or {}

    dockerfile = task_dir / "environment" / "Dockerfile"
    df_lines = 0
    if dockerfile.exists():
        df_lines = sum(1 for _ in dockerfile.read_text().splitlines())

    return TaskMeta(
        task_id=task_dir.name,
        path=task_dir,
        instruction=instruction or task_json.get("description", ""),
        description=task_json.get("description", ""),
        truth=task_json.get("truth", ""),
        difficulty=meta.get("difficulty"),
        category=meta.get("category"),
        tags=list(meta.get("tags") or []),
        agent_timeout_sec=agent.get("timeout_sec"),
        verifier_timeout_sec=verifier.get("timeout_sec"),
        cpus=env.get("cpus"),
        memory_mb=env.get("memory_mb"),
        storage_mb=env.get("storage_mb"),
        has_initial_test=(task_dir / "environment" / "test_initial_state.py").exists(),
        has_final_test=(task_dir / "tests" / "test_final_state.py").exists(),
        has_solve_script=(task_dir / "solution" / "solve.sh").exists(),
        dockerfile_lines=df_lines,
    )


def _tasks_signature() -> tuple[float, int]:
    if not TASKS_DIR.exists():
        return (0.0, 0)
    try:
        mtime = TASKS_DIR.stat().st_mtime
    except OSError:
        mtime = 0.0
    n = sum(1 for _ in TASKS_DIR.iterdir() if _.is_dir())
    return (mtime, n)


@lru_cache(maxsize=4)
def _load_all_tasks_cached(_sig: tuple[float, int]) -> dict[str, TaskMeta]:
    out: dict[str, TaskMeta] = {}
    if not TASKS_DIR.exists():
        return out
    for child in sorted(TASKS_DIR.iterdir()):
        if not child.is_dir() or not child.name.startswith("task_"):
            continue
        meta = _scan_task(child)
        if meta:
            out[meta.task_id] = meta
    return out


def all_tasks() -> dict[str, TaskMeta]:
    return _load_all_tasks_cached(_tasks_signature())


def get_task(task_id: str) -> TaskMeta | None:
    return all_tasks().get(task_id)


# ---------- run scanning --------------------------------------------------- #


_TRIAL_RE = re.compile(r"^(task_\d+_[0-9a-f]+)__([A-Za-z0-9]+)$")


def _scan_trial(run_id: str, trial_dir: Path) -> TrialSummary | None:
    if not trial_dir.is_dir():
        return None
    m = _TRIAL_RE.match(trial_dir.name)
    if not m:
        return None
    task_id = m.group(1)
    rj = _read_json(trial_dir / "result.json") or {}

    reward = None
    vr = rj.get("verifier_result") or {}
    rewards = vr.get("rewards") or {}
    if "reward" in rewards:
        reward = rewards["reward"]

    exc = rj.get("exception_info")
    exc_name = None
    exc_message = None
    exc_tb = None
    if isinstance(exc, dict):
        exc_name = (
            exc.get("exception_type")
            or exc.get("type")
            or exc.get("class")
            or exc.get("name")
        )
        exc_message = exc.get("exception_message") or exc.get("message")
        exc_tb = exc.get("exception_traceback") or exc.get("traceback")
    elif isinstance(exc, str):
        exc_name = exc

    if reward is None:
        rt = _read_text(trial_dir / "verifier" / "reward.txt").strip()
        if rt:
            try:
                reward = float(rt)
            except ValueError:
                reward = None

    agent_result = rj.get("agent_result") or {}
    metadata = agent_result.get("metadata") or {}
    agent_info = rj.get("agent_info") or {}
    model_info = agent_info.get("model_info") or {}

    return TrialSummary(
        run_id=run_id,
        trial_id=trial_dir.name,
        task_id=task_id,
        reward=reward,
        exception=exc_name,
        exception_message=exc_message,
        exception_traceback=exc_tb,
        n_episodes=metadata.get("n_episodes"),
        duration_sec=_parse_iso_duration(rj.get("started_at"), rj.get("finished_at")),
        n_input_tokens=agent_result.get("n_input_tokens"),
        n_output_tokens=agent_result.get("n_output_tokens"),
        n_cache_tokens=agent_result.get("n_cache_tokens"),
        cost_usd=agent_result.get("cost_usd"),
        model_name=model_info.get("name") or agent_info.get("model_name"),
        started_at=rj.get("started_at"),
        finished_at=rj.get("finished_at"),
        path=trial_dir,
    )


def _scan_run(run_dir: Path) -> RunSummary | None:
    if not run_dir.is_dir():
        return None
    cfg = _read_json(run_dir / "config.json") or {}
    res = _read_json(run_dir / "result.json") or {}

    agents = cfg.get("agents") or []
    primary_agent = agents[0] if agents else {}
    datasets = cfg.get("datasets") or []
    dataset_paths = [d.get("path") for d in datasets if d.get("path")]

    stats = res.get("stats") or {}
    evals = stats.get("evals") or {}
    eval_obj: dict[str, Any] = next(iter(evals.values()), {}) if evals else {}
    metrics = eval_obj.get("metrics") or []
    mean_reward = None
    for m in metrics:
        if "mean" in m:
            mean_reward = m["mean"]
            break

    exception_breakdown: dict[str, int] = {}
    exc_stats = eval_obj.get("exception_stats") or {}
    for name, items in exc_stats.items():
        exception_breakdown[name] = len(items)

    summary = RunSummary(
        run_id=run_dir.name,
        root=run_dir,
        started_at=res.get("started_at"),
        finished_at=res.get("finished_at"),
        n_total_trials=res.get("n_total_trials") or stats.get("n_trials") or 0,
        n_errors=stats.get("n_errors") or 0,
        mean_reward=mean_reward,
        model_name=primary_agent.get("model_name"),
        agent_import_path=primary_agent.get("import_path"),
        dataset_paths=dataset_paths,
        n_attempts=cfg.get("n_attempts") or 0,
        exception_breakdown=exception_breakdown,
    )

    trials: list[TrialSummary] = []
    for child in sorted(run_dir.iterdir()):
        if not child.is_dir():
            continue
        if not _TRIAL_RE.match(child.name):
            continue
        ts = _scan_trial(run_dir.name, child)
        if ts:
            trials.append(ts)
    trials.sort(key=lambda t: (t.task_id, t.trial_id))
    summary.trials = trials
    return summary


def _runs_signature() -> tuple[tuple[str, float], ...]:
    parts: list[tuple[str, float]] = []
    for root in RUNS_ROOTS:
        if not root.exists():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            try:
                parts.append((str(child), child.stat().st_mtime))
            except OSError:
                pass
    return tuple(parts)


@lru_cache(maxsize=4)
def _load_all_runs_cached(_sig: tuple[tuple[str, float], ...]) -> dict[str, RunSummary]:
    out: dict[str, RunSummary] = {}
    for root in RUNS_ROOTS:
        if not root.exists():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            run = _scan_run(child)
            if run:
                out[run.run_id] = run
    return out


def all_runs() -> dict[str, RunSummary]:
    return _load_all_runs_cached(_runs_signature())


def get_run(run_id: str) -> RunSummary | None:
    return all_runs().get(run_id)


def get_trial(run_id: str, trial_id: str) -> TrialSummary | None:
    run = get_run(run_id)
    if not run:
        return None
    for t in run.trials:
        if t.trial_id == trial_id:
            return t
    return None


# ---------- per-task aggregation ------------------------------------------ #


@dataclass
class TaskRollup:
    task_id: str
    n_trials: int
    n_pass: int
    n_fail: int
    n_error: int
    pass_rate: float | None
    by_run: dict[str, list[TrialSummary]]


def task_rollup(task_id: str) -> TaskRollup:
    runs = all_runs()
    by_run: dict[str, list[TrialSummary]] = {}
    n_trials = 0
    n_pass = 0
    n_fail = 0
    n_error = 0
    for run in runs.values():
        for t in run.trials:
            if t.task_id != task_id:
                continue
            by_run.setdefault(run.run_id, []).append(t)
            n_trials += 1
            if t.exception:
                n_error += 1
            elif (t.reward or 0) >= 1.0:
                n_pass += 1
            else:
                n_fail += 1
    rate = (n_pass / n_trials) if n_trials else None
    return TaskRollup(
        task_id=task_id,
        n_trials=n_trials,
        n_pass=n_pass,
        n_fail=n_fail,
        n_error=n_error,
        pass_rate=rate,
        by_run=by_run,
    )


def all_task_rollups() -> dict[str, TaskRollup]:
    return {tid: task_rollup(tid) for tid in all_tasks().keys()}


# ---------- model rollup --------------------------------------------------- #


@dataclass
class ModelRollup:
    model_name: str
    pretty_name: str
    n_runs: int
    n_trials: int
    n_pass: int
    n_fail: int
    n_error: int
    pass_rate: float | None
    total_input_tokens: int
    total_output_tokens: int
    runs: list[str]


def model_rollups() -> list[ModelRollup]:
    runs = all_runs()
    by_model: dict[str, list[RunSummary]] = {}
    for run in runs.values():
        key = run.model_name or "unknown"
        by_model.setdefault(key, []).append(run)

    out: list[ModelRollup] = []
    for model, rs in by_model.items():
        n_trials = sum(len(r.trials) for r in rs)
        n_pass = sum(r.n_pass for r in rs)
        n_fail = sum(r.n_fail for r in rs)
        n_error = sum(r.n_error_trials for r in rs)
        rate = (n_pass / n_trials) if n_trials else None
        out.append(
            ModelRollup(
                model_name=model,
                pretty_name=_pretty_model(model),
                n_runs=len(rs),
                n_trials=n_trials,
                n_pass=n_pass,
                n_fail=n_fail,
                n_error=n_error,
                pass_rate=rate,
                total_input_tokens=sum(r.total_input_tokens for r in rs),
                total_output_tokens=sum(r.total_output_tokens for r in rs),
                runs=[r.run_id for r in rs],
            )
        )
    out.sort(key=lambda m: (-(m.pass_rate or 0), -m.n_trials))
    return out


# ---------- trial detail loaders ------------------------------------------ #


def load_trajectory(trial: TrialSummary) -> dict | None:
    return _read_json(trial.path / "agent" / "trajectory.json")


def load_verifier_stdout(trial: TrialSummary) -> str:
    return _read_text(trial.path / "verifier" / "test-stdout.txt")


def load_verifier_reward(trial: TrialSummary) -> str:
    return _read_text(trial.path / "verifier" / "reward.txt")


def load_recording_cast(trial: TrialSummary) -> str:
    return _read_text(trial.path / "agent" / "recording.cast")


def load_dockerfile(task: TaskMeta) -> str:
    return _read_text(task.path / "environment" / "Dockerfile")


def load_initial_test(task: TaskMeta) -> str:
    return _read_text(task.path / "environment" / "test_initial_state.py")


def load_final_test(task: TaskMeta) -> str:
    return _read_text(task.path / "tests" / "test_final_state.py")


def load_solve_script(task: TaskMeta) -> str:
    return _read_text(task.path / "solution" / "solve.sh")


# ---------- aggregate dashboard ------------------------------------------- #


@dataclass
class DashboardStats:
    n_tasks: int
    n_runs: int
    n_trials: int
    n_models: int
    overall_pass_rate: float | None
    runs_sorted: list[RunSummary]
    models: list[ModelRollup]
    hardest_tasks: list[TaskRollup]
    easiest_tasks: list[TaskRollup]
    categories: dict[str, int]
    difficulties: dict[str, int]
    tags: dict[str, int]


def dashboard_stats() -> DashboardStats:
    tasks = all_tasks()
    runs = all_runs()
    rollups = all_task_rollups()

    n_trials = sum(len(r.trials) for r in runs.values())
    n_pass = sum(r.n_pass for r in runs.values())

    categories: dict[str, int] = {}
    difficulties: dict[str, int] = {}
    tags: dict[str, int] = {}
    for t in tasks.values():
        if t.category:
            categories[t.category] = categories.get(t.category, 0) + 1
        if t.difficulty:
            difficulties[t.difficulty] = difficulties.get(t.difficulty, 0) + 1
        for tag in t.tags:
            tags[tag] = tags.get(tag, 0) + 1

    rated = [r for r in rollups.values() if r.n_trials and r.pass_rate is not None]
    hardest = sorted(rated, key=lambda r: (r.pass_rate or 0, -r.n_trials))[:10]
    easiest = sorted(rated, key=lambda r: (-(r.pass_rate or 0), -r.n_trials))[:10]

    runs_sorted = sorted(
        runs.values(),
        key=lambda r: r.started_at or "",
        reverse=True,
    )

    return DashboardStats(
        n_tasks=len(tasks),
        n_runs=len(runs),
        n_trials=n_trials,
        n_models=len({r.model_name for r in runs.values() if r.model_name}),
        overall_pass_rate=(n_pass / n_trials) if n_trials else None,
        runs_sorted=runs_sorted,
        models=model_rollups(),
        hardest_tasks=hardest,
        easiest_tasks=easiest,
        categories=categories,
        difficulties=difficulties,
        tags=tags,
    )
