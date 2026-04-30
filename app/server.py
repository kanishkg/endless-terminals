"""Flask app for browsing tasks, solutions, and model performance.

Run with:

    python -m app.server               # http://127.0.0.1:5050
    python -m app.server --port 8000

The app reads everything from `harbor_tasks/` and `solution_sonnet/` on the
local filesystem; no database is required.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from typing import Any

from flask import Flask, abort, jsonify, render_template, request, url_for

from app import data


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.jinja_env.add_extension("jinja2.ext.do")

    @app.template_filter("ts")
    def _ts_filter(value: str | None) -> str:
        if not value:
            return "—"
        return value.replace("T", " ").replace("Z", "").split(".")[0]

    @app.template_filter("dur")
    def _dur_filter(value: float | int | None) -> str:
        if value is None:
            return "—"
        v = float(value)
        if v < 1:
            return f"{v * 1000:.0f}ms"
        if v < 60:
            return f"{v:.1f}s"
        m, s = divmod(v, 60)
        if m < 60:
            return f"{int(m)}m {int(s)}s"
        h, m = divmod(m, 60)
        return f"{int(h)}h {int(m)}m"

    @app.template_filter("intcomma")
    def _intcomma(value: int | float | None) -> str:
        if value is None:
            return "—"
        try:
            return f"{int(value):,}"
        except (TypeError, ValueError):
            return str(value)

    @app.template_filter("pct")
    def _pct(value: float | None, digits: int = 1) -> str:
        if value is None:
            return "—"
        return f"{value * 100:.{digits}f}%"

    @app.template_filter("short_id")
    def _short_id(value: str) -> str:
        if not value:
            return ""
        return value.split("__")[-1]

    @app.template_filter("short_task")
    def _short_task(value: str) -> str:
        if not value:
            return ""
        return value.replace("task_000000_", "")

    @app.context_processor
    def inject_globals():
        return {
            "all_runs": data.all_runs,
        }

    # -------- pages ------------------------------------------------------- #

    @app.get("/")
    def index():
        stats = data.dashboard_stats()
        return render_template("index.html", stats=stats)

    @app.get("/runs")
    def runs_index():
        runs = sorted(
            data.all_runs().values(),
            key=lambda r: r.started_at or "",
            reverse=True,
        )
        return render_template("runs.html", runs=runs)

    @app.get("/runs/<run_id>")
    def run_detail(run_id: str):
        run = data.get_run(run_id)
        if not run:
            abort(404)

        # Group trials by task
        by_task: dict[str, list] = {}
        for t in run.trials:
            by_task.setdefault(t.task_id, []).append(t)

        task_rows = []
        for tid, trials in by_task.items():
            n_pass = sum(1 for t in trials if (t.reward or 0) >= 1.0)
            n_err = sum(1 for t in trials if t.exception)
            n_total = len(trials)
            pass_rate = n_pass / n_total if n_total else None
            tasks = data.all_tasks()
            meta = tasks.get(tid)
            task_rows.append(
                {
                    "task_id": tid,
                    "trials": trials,
                    "n_pass": n_pass,
                    "n_total": n_total,
                    "n_err": n_err,
                    "pass_rate": pass_rate,
                    "meta": meta,
                }
            )
        task_rows.sort(key=lambda r: (r["pass_rate"] or 0, r["task_id"]))

        # Token / duration aggregates
        durations = [t.duration_sec for t in run.trials if t.duration_sec]
        avg_duration = sum(durations) / len(durations) if durations else None

        return render_template(
            "run.html",
            run=run,
            task_rows=task_rows,
            avg_duration=avg_duration,
        )

    @app.get("/tasks")
    def tasks_index():
        tasks = list(data.all_tasks().values())
        rollups = data.all_task_rollups()

        category = request.args.get("category", "").strip() or None
        difficulty = request.args.get("difficulty", "").strip() or None
        tag = request.args.get("tag", "").strip() or None
        q = request.args.get("q", "").strip().lower() or None
        sort = request.args.get("sort", "id")

        if category:
            tasks = [t for t in tasks if t.category == category]
        if difficulty:
            tasks = [t for t in tasks if t.difficulty == difficulty]
        if tag:
            tasks = [t for t in tasks if tag in (t.tags or [])]
        if q:
            tasks = [
                t
                for t in tasks
                if q in (t.instruction or "").lower()
                or q in (t.task_id or "").lower()
                or q in (t.description or "").lower()
            ]

        def _row(t: data.TaskMeta):
            r = rollups.get(t.task_id)
            return {
                "meta": t,
                "rollup": r,
            }

        rows = [_row(t) for t in tasks]

        def _has_trials(row) -> bool:
            return bool(row["rollup"] and row["rollup"].n_trials)

        if sort == "pass_desc":
            rows.sort(
                key=lambda r: (
                    not _has_trials(r),
                    -((r["rollup"].pass_rate if _has_trials(r) else 0) or 0),
                    r["meta"].task_id,
                )
            )
        elif sort == "pass_asc":
            rows.sort(
                key=lambda r: (
                    not _has_trials(r),
                    (r["rollup"].pass_rate if _has_trials(r) else 1) or 0,
                    r["meta"].task_id,
                )
            )
        elif sort == "trials":
            rows.sort(key=lambda r: (-(r["rollup"].n_trials or 0), r["meta"].task_id))
        else:
            rows.sort(key=lambda r: r["meta"].task_id)

        all_tasks = list(data.all_tasks().values())
        categories = sorted({t.category for t in all_tasks if t.category})
        difficulties = sorted({t.difficulty for t in all_tasks if t.difficulty})
        all_tags: Counter[str] = Counter()
        for t in all_tasks:
            for tg in t.tags or []:
                all_tags[tg] += 1

        return render_template(
            "tasks.html",
            rows=rows,
            categories=categories,
            difficulties=difficulties,
            all_tags=all_tags.most_common(40),
            current={
                "category": category,
                "difficulty": difficulty,
                "tag": tag,
                "q": q or "",
                "sort": sort,
            },
        )

    @app.get("/tasks/<task_id>")
    def task_detail(task_id: str):
        meta = data.get_task(task_id)
        if not meta:
            abort(404)
        rollup = data.task_rollup(task_id)
        runs = data.all_runs()
        per_run_trials = []
        for run_id, trials in rollup.by_run.items():
            run = runs.get(run_id)
            per_run_trials.append({"run": run, "trials": trials})
        per_run_trials.sort(key=lambda r: r["run"].started_at if r["run"] else "")

        dockerfile = data.load_dockerfile(meta)
        initial_test = data.load_initial_test(meta) if meta.has_initial_test else ""
        final_test = data.load_final_test(meta) if meta.has_final_test else ""
        solve = data.load_solve_script(meta) if meta.has_solve_script else ""

        return render_template(
            "task.html",
            meta=meta,
            rollup=rollup,
            per_run_trials=per_run_trials,
            dockerfile=dockerfile,
            initial_test=initial_test,
            final_test=final_test,
            solve=solve,
        )

    @app.get("/runs/<run_id>/trials/<trial_id>")
    def trial_detail(run_id: str, trial_id: str):
        trial = data.get_trial(run_id, trial_id)
        if not trial:
            abort(404)
        meta = data.get_task(trial.task_id)
        run = data.get_run(run_id)
        traj = data.load_trajectory(trial) or {}
        verifier_stdout = data.load_verifier_stdout(trial)
        reward_txt = data.load_verifier_reward(trial)

        # Transform trajectory steps for template-friendly rendering
        steps_view: list[dict[str, Any]] = []
        for s in traj.get("steps", []):
            view = {
                "step_id": s.get("step_id"),
                "timestamp": s.get("timestamp"),
                "source": s.get("source"),
                "model_name": s.get("model_name"),
                "message": s.get("message"),
                "tool_calls": s.get("tool_calls") or [],
                "observation": s.get("observation") or {},
                "metrics": s.get("metrics") or {},
            }
            steps_view.append(view)

        # Sibling trials for navigation
        siblings = []
        if run:
            sibs = [t for t in run.trials if t.task_id == trial.task_id]
            sibs.sort(key=lambda t: t.trial_id)
            for i, t in enumerate(sibs):
                if t.trial_id == trial_id:
                    prev_t = sibs[i - 1] if i > 0 else None
                    next_t = sibs[i + 1] if i + 1 < len(sibs) else None
                    siblings = sibs
                    break
            else:
                prev_t = None
                next_t = None
        else:
            prev_t = next_t = None

        return render_template(
            "trial.html",
            trial=trial,
            meta=meta,
            run=run,
            traj=traj,
            steps=steps_view,
            verifier_stdout=verifier_stdout,
            reward_txt=reward_txt,
            siblings=siblings,
            prev_t=prev_t,
            next_t=next_t,
        )

    # -------- raw JSON / file endpoints ----------------------------------- #

    @app.get("/runs/<run_id>/trials/<trial_id>/cast")
    def trial_cast(run_id: str, trial_id: str):
        trial = data.get_trial(run_id, trial_id)
        if not trial:
            abort(404)
        cast = data.load_recording_cast(trial)
        return (cast, 200, {"Content-Type": "text/plain; charset=utf-8"})

    @app.get("/api/dashboard.json")
    def api_dashboard():
        s = data.dashboard_stats()
        return jsonify(
            {
                "n_tasks": s.n_tasks,
                "n_runs": s.n_runs,
                "n_trials": s.n_trials,
                "n_models": s.n_models,
                "overall_pass_rate": s.overall_pass_rate,
                "models": [
                    {
                        "model_name": m.model_name,
                        "pretty": m.pretty_name,
                        "pass_rate": m.pass_rate,
                        "n_trials": m.n_trials,
                        "n_pass": m.n_pass,
                        "n_fail": m.n_fail,
                        "n_error": m.n_error,
                    }
                    for m in s.models
                ],
            }
        )

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Endless Terminals UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
