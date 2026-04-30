"""Ask GPT for a task‑description *template* + parameter schema."""
from __future__ import annotations

import json
import uuid
import random
import re
from pathlib import Path
import sys
from typing import Optional

sys.path.insert(0, str(Path().resolve()))

from generator import chat_completion_batch

SYSTEM_MSG = """You are creating realistic Linux-terminal tasks for training an AI agent.

Respond in xml format.

<task>
    The task as a human would write it. See the voice guide below.
    Lengths vary. Many should be under 50 words; 180 is a ceiling, not a target.
    Real Slack messages are short. Lean shorter than feels comfortable.
    Do NOT hand the agent a numbered list of steps or sub-requirements.
    Do NOT directly give the commands or the fix recipe.
</task>

<truth>
    Privileged ground-truth for the grader. Never appears in <task>.
    Use the template described in the "truth block" section below.
</truth>

# How tasks open

Real engineering requests come in several shapes. Rotate across them deliberately — don't default to "something broke, fix it."

- **Trigger / debug.** "I was rebasing when…", "The nightly ETL started returning…", "I just pulled main and now…". Something is already underway and broken.
- **Build / setup / creation.** "I need a working X by EOD." A construction task with constraints, no failure backstory required.
- **Reverse-engineering.** "There's this binary nobody documented and I need to talk to it." Exploratory, curiosity-driven.
- **Recovery.** "My DB got truncated, I have a partial backup, help me get back what I can."
- **Migration / port.** "We're moving from X to Y and I'm stuck on Z."
- **Investigation.** "The numbers in the report don't match the source. Figure out which is right."
- **Optimization / tightening.** "This loop is fine but it's 40x slower than it should be."

The first sentence should drop the agent into a situation, not announce a project. Past tense and present continuous both work ("started failing", "is silently dropping rows"). Cold openings ("Need a Python client for…") are also fine for non-debug task types.

# Voice

The narrator is an engineer mid-stream. Casual, possibly tired, possibly wrong.

- **First-person, mid-flow.** No greetings, no project briefs, no "Hi Claude," no "Please complete the following task."
- **Specific about *where*, vague about *why*.** Be exact with paths, filenames, ports, table names, commit shas, version numbers. Be loose, hedging, or even mistaken about diagnosis. The user's guess can be wrong — that's realistic and forces real diagnosis.
- **Hedges welcome.** "this feels like a timezone thing", "might be middleware idk", "nothing's changed afaik".
- **Register cues for messiness.** Dropped articles ("server keeps OOMing"), abbreviations ("repo", "k8s", "tf", "ngl", "afaict"), trailing parentheticals ("(or maybe not)"), incomplete memory ("didn't save the exact error"), tangents, sentence fragments. Don't make every task this informal — vary it — but most should have at least one such tell. Maintain proper capitalization and punctuation — the messiness comes from tone and content, not from breaking grammar rules. Keep the subject pronoun "I" — write "I've been trying to…", "I have a tarball at…", "I'm getting…", not the pronoun-dropped forms "Been trying to…", "Got a tarball at…", "Trying to get…". Dropping "I" reads like a log entry, not a person talking.
- **One imperfection minimum.** Each task must contain at least one of: a vague description, an incomplete memory, a soft guess that may be wrong, slight rambling, or a tangent.

# What real users don't do

The deepest tell that a task was written for a grader is when the user seems suspiciously aware of how it'll be verified. Catch the whole family of these tells, not just specific examples. Real users:

- Don't request artifacts whose only purpose is grading ("write a log of every change you made", "produce a report listing all actions taken").
- Don't specify exact output formats down to whitespace and line counts unless there's a real downstream reason (e.g. another tool consumes it).
- Don't restate verification criteria ("the grader will run `foo --bar` and check Z").
- Don't enumerate sub-requirements as a numbered or bulleted list inside the ask.
- Don't explain the root cause cleanly — they're asking *because* they don't know it.
- Don't dictate implementation ("use pandas, name the function `clean_data`") unless a real engineer would actually constrain that (locked-down env, existing convention, perf reason).

If the task body reads like a Jira ticket, spec, or piece of documentation, rewrite it.

Banned phrasings (these are tells; do not use):
- "The output should…"
- "The file must contain…"
- "Ensure that…"
- "Line 1: …", "Step 1: …"
- "Return a JSON with the following fields…"
- "Please complete the following task"

# Prose, not specification

The task is one or two paragraphs of prose, not a list of requirements. A constraint that would normally be a bullet point gets folded into a sentence, or dropped if the agent could reasonably infer it from context.

Bad: "It should output a JSON with fields timestamp, services, and overall status."
    — banned phrasing ("should output"), spec voice, reads like API docs.

Good: "throw it into a json report — timestamp, services, overall status, the usual."
    — same information, casual register, sounds like Slack.

If you find yourself listing requirements, you've stopped writing as a user and started writing as a PM. Rewrite as one breath of prose instead. The fix is almost always voice, not deletion — keep the concrete observables (paths, counts, error fragments, ports), kill the spec register around them.

## Bundling

Do NOT express requirements as multiple consecutive sentences. If you have three short sentences each stating a requirement, merge them into one.

Bad: "It should write a report. It should include timestamps. It should include results."
    — three requirement sentences in a row. Spec rhythm.

Good: "need a quick report dumped somewhere — timestamps, results, that kind of thing."
    — same info, single breath, conversational.

## Structural red flags

If your draft contains any of the following patterns, it's too structured and you must rewrite it as flowing prose:

- More than one sentence starting with "It should…", "The script should…", "The output should…"
- Repeated imperative verbs at sentence-start ("Add X. Create Y. Ensure Z.")
- Sequential instructions that read as numbered steps even without numbers
- A bullet or dash-list of requirements inside the task body
- Any sentence that sounds like a function docstring

# The truth block

This is where grading lives. Be exhaustive — vague truth blocks produce ungradable tasks. Use roughly this shape:

- **Initial state.** What's pre-seeded on disk. Exact paths. Which files are writable vs read-only. What tools/binaries/services exist. What's already running. Versions where they matter. Any subtle setup details that affect the bug.
- **Expected final state.** Positive checks the grader will run: file contents, exit codes, service responses, test pass/fail, process state. Be specific — "exits 0 and prints exactly X" not "works correctly."
- **Invariants.** What must NOT change. Unrelated files unchanged, versions not downgraded, parameters preserved, source byte-identical, the still-running daemon still running, etc.
- **Anti-shortcut guards.** When a task is solvable by cheating (hardcoding the answer, deleting the failing test, shelling out to the binary instead of speaking its protocol, reverting to an older version, replacing the config with a stub), spell out a grader check that catches it. The licensed-daemon example's `grep` check is the canonical pattern.

Values in <truth> must NOT appear in <task>. If the agent could solve the task by reading the truth block alone, you've leaked.

# Domain and task-type variety

Rotate deliberately across domains. A non-exhaustive list:

Frontend & build tooling, backend services, data engineering & ETL, scientific computing, ML training/inference, systems & low-level (C, ELF, syscalls, kernel modules), DevOps & infra, security & forensics, data recovery, legacy maintenance, text/log processing, embedded, distributed systems, networking, graphics.

Rotate task *types*: debugging, recovering, creating, migrating, reverse-engineering, optimizing, porting, investigating. Models tend to collapse toward "Python data bug" — actively resist it. If you've already produced 3 backend-debug tasks in a row, the next one should be from a different quadrant.

Vary the deliverable. Not every task ends in a text report. Mix:
- A running service that responds correctly to a curl
- A script that exits 0 with the right output
- A codebase where a test suite passes
- A process state change (rogue process killed, daemon up)
- A system config (permissions, cron, env vars, mount)
- A file with correct semantic content (valid JSON with required keys, correct row count, etc.)
- Recovered data that matches a known-good reference
- A binary that can be run and behaves correctly

# Environment constraints

- The agent does NOT have root. Anything to be modified must be writable by a normal user in the seeded state.
- Use absolute paths. Home is /home/user.
- No live internet. No current-events knowledge.
- No command-count limits. The agent has a real shell across many turns.
- Tasks are grounded in pre-seeded state fully described in <truth>. Never start from an empty filesystem.
- The environment is a single Docker container (ubuntu:22.04). The following are NOT available and must NOT be required:
  - Docker, Podman, or any container runtime (no Docker-in-Docker)
  - Kubernetes, kind, minikube, or any orchestration tool
  - systemd, init systems, or service managers (services must be started directly as background processes)
  - Multiple networked hosts or containers
  - Privileged kernel operations (loading kernel modules, mounting filesystems, modifying iptables/nftables)
  - GUI, display server, or graphical applications
- Services like databases (PostgreSQL, MySQL, Redis) CAN be used but must be started as foreground/background processes via a wrapper script or CMD entrypoint — not via systemctl or pg_ctl with cluster init. The Dockerfile must handle all service initialization so the service is running when the agent starts.

# A bad task, annotated

Here's what NOT to do:

<task>
    Please complete the following task:
    1. There is a Python script at /home/user/etl/run.py that processes a CSV.
    2. The script has a timezone bug on line 47 where it uses naive datetimes instead of UTC-aware ones.
    3. Fix the bug by importing pytz and converting timestamps to UTC.
    4. The output file /home/user/etl/out.csv should contain exactly 11 rows.
    5. Also write a log at /home/user/etl/fix.log documenting every change you made.
    The grader will run `python /home/user/etl/run.py` and check the row count.
</task>

What's wrong:
- "Please complete the following task" — banned greeting. Real users don't write this.
- Numbered list of requirements — Jira ticket, not Slack.
- Root cause leaked ("timezone bug on line 47, naive datetimes") — nothing to diagnose.
- Implementation dictated ("import pytz") — no reason given.
- Grader-tell artifact ("write a log documenting every change") — no real user wants this.
- Verification criteria restated ("the grader will run X and check Y") — leaks the test.
- "Should contain exactly 11 rows" belongs in <truth>, not <task>.
- Clean punctuation, full paragraph, no hedge, no register messiness — reads like a worksheet.

A real version of the same task:

<task>
    Nightly ETL on /home/user/etl/run.py is dropping rows again — supposed to write 11 to out.csv and I'm getting 5. Think it might be a tz thing? We just moved the source data over from the old box which was on PT and ours is UTC, so maybe related. Anyway need it actually emitting all 11.
</task>

Why this works: trigger event (dropping rows), specific observables (5 vs 11), a guess that *might* be wrong (timezone — could be that, could be filtering, could be something else entirely), casual register, no instruction list, no implementation prescription, no grader leak.

# Good examples

<example>
<task>
    Bumped vite 4.5 -> 5 in /home/user/dashboard last night (and the react plugin with it) and now `npm run build` falls over partway — something about "default" not being exported, then later some `@/` imports can't be resolved. Weird thing is `npm run dev` still works fine. Haven't touched vite.config.ts in months.
    Just need the prod build green again — usual dist output, working index.html.
</task>

<truth>
    Initial state:
    - /home/user/dashboard is a React + TypeScript app using Vite.
    - package.json has "vite": "^5.0.0", "@vitejs/plugin-react": "^4.2.0", and "type": "module".
    - node_modules is already installed. Node 20.x and npm available.
    - /home/user/dashboard/vite.config.ts is in CommonJS form:
        const { defineConfig } = require('vite');
        const react = require('@vitejs/plugin-react');
        const path = require('path');
        module.exports = defineConfig({
            plugins: [react()],
            resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
        });
    - Two problems exposed by Vite 5 + "type": "module":
        (a) the file uses CommonJS constructs (require, module.exports, __dirname) which don't work when the config is loaded as ESM.
        (b) @vitejs/plugin-react v4 exports a default — must be imported as default, not require-as-namespace.
    - src/App.tsx and several files under src/components and src/lib import from `@/…` aliased paths.
    - `npm run dev` succeeds. `npm run build` fails.
    - /home/user/dashboard is writable.

    Expected final state:
    - `cd /home/user/dashboard && npm run build` exits 0.
    - /home/user/dashboard/dist/index.html exists.
    - dist contains at least one hashed JS bundle referenced by index.html, and every asset path referenced by index.html exists on disk.
    - The Vite config still lives at vite.config.ts OR vite.config.{js,mjs,cjs}, used by the build (not replaced with a stub that drops the alias).
    - `@` alias still resolves to /home/user/dashboard/src — verified by src files importing from `@/…` successfully bundling into dist.

    Invariants:
    - package.json vite version still on ^5.x (not downgraded).
    - src/ source code byte-identical to its initial state.

    Anti-shortcut guards:
    - The build must succeed against a real config that preserves the `@` alias, not a stripped-down replacement.
</truth>
</example>

<example>
<task>
    Energy isn't conserving in /home/user/sim/orbit.py — rk4, dt=0.01, near-circular two-body. Drift's about 0.3% per 10k steps which is way too much for numerical noise at this dt, and halving dt doesn't help. So I don't think it's just integrator accuracy — something's actually wrong in the physics or the stepping.
    Find the bug. Don't paper over it by shrinking dt or swapping integrators.
</task>

<truth>
    Initial state:
    - /home/user/sim/orbit.py simulates two point masses under Newtonian gravity with classical fixed-step RK4.
    - Parameters: m1=1.0, m2=1.0, G=1.0, dt=0.01, N_STEPS=100_000. Initial r1=[1,0], r2=[-1,0]; v1=[0, 0.5], v2=[0, -0.5].
    - The bug is in the acceleration function. It computes the force on body 1 correctly, then assigns `a2 = a1` instead of Newton's-third-law `a2 = -a1 * (m1/m2)`. That injects a spurious net external force, the center of mass accelerates, and total energy drifts upward — about 0.3% per 10k steps, ~3% over the full run.
    - The RK4 integrator itself (k1..k4 weighting and state update) is correct.
    - Energy printed at start and end with labels "initial E =" and "final E =".
    - numpy installed. Python 3.11+. /home/user/sim writable.

    Expected final state:
    - `python /home/user/sim/orbit.py` prints the two energy lines, and |final - initial| <= 1e-6.
    - Fix lives in /home/user/sim/orbit.py and is small/local — not a rewrite.

    Invariants:
    - dt remains 0.01, N_STEPS remains 100_000.
    - Integrator stays RK4 (no swap to leapfrog/Verlet/symplectic-Euler/adaptive).
    - Initial conditions (masses, G, positions, velocities) unchanged.
    - Output still contains "initial E =" and "final E =" lines, in that order.

    Anti-shortcut guards:
    - The fix must address the underlying physics error, not artificially clamp/rescale energy at the end of the run, and not reduce N_STEPS.
</truth>
</example>

<example>
<task>
    There's a daemon at /opt/tools/licensed that ops relies on — author left years ago, source gone, binary stripped. Listens on /run/licensed.sock, you send it something and it gives back a license token. Need a python client at /home/user/client.py that asks for a token for user 4217 and prints it.
    You'll have to figure out the wire format yourself. Daemon is up so you can poke the socket.
</task>

<truth>
    Initial state:
    - /opt/tools/licensed is a stripped x86-64 ELF (gcc -O2). Currently running, listening on AF_UNIX /run/licensed.sock. World-readable, NOT writable by the agent.
    - /run/licensed.sock is rw by the agent user.
    - Wire protocol (discoverable via strings/objdump/ltrace/gdb and by poking the socket):
        Request (12 bytes): magic "LIC\\0" (4B) || user_id (uint32 LE) || nonce (uint32 LE; client-chosen).
        Response: magic "LIC\\0" (4B) || user_id (uint32 LE, echo) || nonce (uint32 LE, echo) || length L (uint8) || token (L bytes ASCII).
    - Token deterministic per user id. For user 4217 the token is the 16-byte ASCII string "TK-4217-ea91f2c4". Same token every call.
    - Available: python3 with socket and struct stdlib; gcc, objdump, strings, ltrace, strace, gdb, readelf, xxd. No ghidra.
    - /home/user is writable. /home/user/client.py does not exist initially.
    - Agent cannot restart, modify, or replace /opt/tools/licensed.

    Expected final state:
    - /home/user/client.py exists.
    - `python3 /home/user/client.py` connects to /run/licensed.sock, performs the protocol exchange for user 4217, and prints exactly TK-4217-ea91f2c4 followed by a single newline. stderr empty or informational. Exit 0.

    Anti-shortcut guards:
    - `grep -E 'subprocess|os\\.system|os\\.popen|/opt/tools/licensed|TK-4217-ea91f2c4' /home/user/client.py` must return no match. The token must come over the socket, not be hardcoded; the client must speak the protocol, not shell out or read the binary directly.

    Invariants:
    - Daemon still running on /run/licensed.sock after the task.
    - /opt/tools/licensed byte-identical to its initial state.
</truth>
</example>

# Self-check before finalizing

After drafting, ask:

1. Does the first sentence drop the agent into a situation, or announce a project?
2. Is there at least one imperfection (vague phrase, hedge, possibly-wrong guess, dropped article, abbreviation)?
3. Could a real engineer plausibly send this in Slack, or does it read like a worksheet?
4. Have I leaked the diagnosis or the fix recipe?
5. Are any banned phrasings present ("The output should", "Ensure that", "Step 1:", "Please complete", etc.)?
6. Is the task prose, or did I slip into spec voice / a list of requirements / consecutive "It should…" sentences / repeated sentence-initial imperatives?
7. Is the deliverable something a real user would actually want, or is it graderware (a log of changes, a report of actions taken)?
8. Does <truth> contain initial state, expected final state, invariants, AND anti-shortcut guards where relevant?
9. Am I producing the same domain or task type as my recent outputs? If so, switch.

If any answer is wrong, rewrite. Output only the final version.
"""


# --- User-message template & combinatorial variation helpers ---------------------------------

# Template with placeholders that can be filled combinatorially to diversify the prompt sent to
# the language model.  Each run of this script will randomly choose values from the option sets
# below, providing a broad variety of task prompts.

# --- Task inspiration for diversity ---
TASK_CATEGORIES = [
    "file and directory management",
    "text processing and manipulation",
    "system monitoring and diagnostics",
    "package management",
    "user and permission management",
    "network diagnostics",
    "log analysis",
    "backup and archiving",
    "process management",
    "disk usage analysis",
    "environment configuration",
    "data transformation",
    "scheduled tasks and cron jobs",
    "service configuration",
    "database operations",
    "container management",
    "git repository operations",
    "security scanning",
    "performance benchmarking",
    "remote file synchronization",
    "API testing and curl operations",
    "certificate management",
    "DNS and hostname resolution",
    "firewall configuration",
    "shell scripting automation",
    "symbolic link management",
    "file compression and extraction",
    "checksum verification",
    "text encoding conversions",
    "CSV/JSON data manipulation",
    "YAML and TOML configuration editing",
    "INI configuration parsing",
    "regex-based log filtering",
    "SQLite database operations via CLI",
    "SSH keypair generation and management",
    "GPG file encryption and signature verification",
    "time zone and locale configuration",
    "cron and systemd timer authoring (user)",
    "Python virtual environment setup with venv",
    "pip package environment management",
    "git submodule management",
    "semantic version bumping and changelogs",
    "Makefile authoring and task automation",
    "text diffing and patch application",
    "markdown documentation generation and linting",
    "environment variable and dotenv management",
    "JSON schema validation and jq processing",
    "find and xargs batch file operations",
    "awk and sed text processing",
    "sort and uniq frequency counting",
    "cut and paste column manipulation",
    "complex permissions management",
    "dev environment setup",
    "headless browser data scraping",
    "distributed system debugging",
    "data pipeline with error recovery",
    "exploiting/fixing security vulnerabilities",
    "performance optimization",
    "running old code",
    "database migration with data validation",
    "launch a webserver",
    "optimization solvers"
]


CATEGORY_BUCKETS = {
    "file_ops": [
        "file and directory management",
        "symbolic link management",
        "file compression and extraction",
        "checksum verification",
        "find and xargs batch file operations",
        "backup and archiving",
    ],
    "networking": [
        "network diagnostics",
        "DNS and hostname resolution",
        "firewall configuration",
        "remote file synchronization",
        "API testing and curl operations",
    ],
    "services": [
        "service configuration",
        "launch a webserver",
        "container management",
        "scheduled tasks and cron jobs",
        "cron and systemd timer authoring (user)",
    ],
    "security": [
        "security scanning",
        "exploiting/fixing security vulnerabilities",
        "GPG file encryption and signature verification",
        "SSH keypair generation and management",
        "certificate management",
        "complex permissions management",
    ],
    "debugging": [
        "distributed system debugging",
        "performance optimization",
        "running old code",
        "data pipeline with error recovery",
    ],
    "data_processing": [
        "data transformation",
        "CSV/JSON data manipulation",
        "database operations",
        "SQLite database operations via CLI",
        "database migration with data validation",
        "JSON schema validation and jq processing",
    ],
    "git_ops": [
        "git repository operations",
        "git submodule management",
        "semantic version bumping and changelogs",
        "text diffing and patch application",
    ],
    "system_admin": [
        "process management",
        "user and permission management",
        "system monitoring and diagnostics",
        "disk usage analysis",
        "environment configuration",
        "time zone and locale configuration",
        "environment variable and dotenv management",
    ],
    "build_tools": [
        "Makefile authoring and task automation",
        "dev environment setup",
        "Python virtual environment setup with venv",
        "pip package environment management",
        "package management",
        "optimization solvers",
    ],
    "text_processing": [
        "text processing and manipulation",
        "log analysis",
        "regex-based log filtering",
        "awk and sed text processing",
        "sort and uniq frequency counting",
        "cut and paste column manipulation",
        "text encoding conversions",
        "YAML and TOML configuration editing",
        "INI configuration parsing",
        "markdown documentation generation and linting",
        "headless browser data scraping",
        "shell scripting automation",
    ],
}

DIFFICULTY_GUIDANCE = {
    "easy": (
        "The task has a single, obvious cause and a direct fix. No diagnosis required — "
        "the user knows what's wrong or what they want, and the agent just needs to execute. "
        "One tool, one concept, one step of reasoning. "
        "Examples: fix a known typo in a config file, extract a specific field from a log with grep, "
        "kill a process on a given port, create a directory structure from a spec, chmod a file."
    ),
    "medium": (
        "The task requires investigation before action — the root cause isn't handed to the agent. "
        "Multiple tools or files are involved, and the agent must connect information across them. "
        "There's at least one non-obvious step: reading an error to figure out which config is wrong, "
        "tracing a failure through 2-3 files, or combining outputs from different commands. "
        "Examples: a service won't start and the agent must read logs to find the misconfigured setting, "
        "data is malformed and the agent must figure out which transformation step corrupts it, "
        "a build fails and the agent must identify the dependency conflict from error output."
    ),
    "hard": (
        "The task requires domain expertise, multi-system reasoning, or diagnosing subtle/misleading bugs. "
        "What makes it hard is NOT length — it's that naive approaches fail, obvious guesses are wrong, "
        "or multiple interacting components must be understood together. "
        "At least one of these properties must hold:\n"
        "- The symptom misleads: the error points to X but the real cause is Y (e.g. energy drift that looks like integrator error but is a physics bug).\n"
        "- Fixing one thing breaks another: the agent must satisfy multiple constraints simultaneously.\n"
        "- Domain knowledge is required: understanding a wire protocol, a file format, a concurrency primitive, or an algorithm.\n"
        "- The state space is large: multiple config files, processes, or data flows must be traced to find the one failure point.\n"
        "- Reverse engineering is needed: no documentation, the agent must probe/inspect to discover behavior.\n"
        "Examples: a race condition that only manifests under specific timing, a corrupted binary file "
        "that must be partially reconstructed using format knowledge, a service that works in dev but fails "
        "in the container due to a subtle environment difference, an optimization problem where the obvious "
        "O(n^2) approach times out and the agent must find the algorithmic insight."
    ),
}



SCENARIO_CONTEXTS = [
    "developer organizing project files",
    "system administrator maintaining servers",
    "data analyst processing CSV files",
    "DevOps engineer debugging logs",
    "security auditor checking permissions",
    "backup administrator archiving data",
    "researcher organizing datasets",
    "web developer",
    "database administrator optimizing queries",
    "network engineer troubleshooting connectivity",
    "release manager preparing deployments",
    "QA engineer setting up test environments",
    "cloud architect migrating services",
    "site reliability engineer monitoring uptime",
    "data engineer building ETL pipelines",
    "compliance officer auditing systems",
    "technical writer organizing documentation",
    "machine learning engineer preparing training data",
    "penetration tester scanning vulnerabilities",
    "infrastructure engineer automating provisioning",
    "support engineer collecting diagnostics",
    "build engineer managing artifacts",
    "configuration manager tracking changes",
    "capacity planner analyzing resource usage",
    "incident responder investigating issues",
    "automation specialist creating workflows",
    "integration developer testing APIs",
    "performance engineer profiling applications",
    "container specialist managing microservices",
    "backup engineer verifying data integrity",
    "monitoring specialist setting up alerts",
    "deployment engineer rolling out updates",
    "storage administrator managing disk space",
    "log analyst investigating patterns",
    "script developer creating utilities",
    "observability engineer tuning dashboards",
    "data scientist cleaning datasets",
    "site administrator managing user accounts",
    "operations engineer triaging incidents",
    "IT support technician resolving tickets",
    "platform engineer maintaining CI/CD pipelines",
    "FinOps analyst optimizing cloud costs",
    "DevSecOps engineer enforcing policy as code",
    "localization engineer updating translations",
    "MLOps engineer tracking experiment artifacts",
    "edge computing engineer deploying to IoT devices",
    "mobile build engineer maintaining pipelines",
    "security engineer rotating credentials",
    "compliance analyst generating audit trails",
    "backup operator testing restores",
    "database reliability engineer managing backups",
    "linux systems engineer hardening configurations",
    "kubernetes operator managing manifests",
    "artifact manager curating binary repositories",
]

def pick_balanced_categories(n: int) -> list[str]:
    """Pick n categories with balanced bucket coverage via round-robin, then random fill."""
    bucket_names = list(CATEGORY_BUCKETS.keys())
    random.shuffle(bucket_names)
    categories: list[str] = []
    for i in range(n):
        bucket = bucket_names[i % len(bucket_names)]
        categories.append(random.choice(CATEGORY_BUCKETS[bucket]))
    return categories


def pick_difficulties(n: int, difficulty: str, distribution: Optional[dict[str, float]] = None) -> list[str]:
    """Pick n difficulty levels based on mode. 'mixed' uses the distribution dict."""
    if difficulty != "mixed":
        return [difficulty] * n
    dist = distribution or {"easy": 0.2, "medium": 0.5, "hard": 0.3}
    levels = list(dist.keys())
    weights = [dist[k] for k in levels]
    return random.choices(levels, weights=weights, k=n)


def random_user_msg(category: Optional[str] = None, difficulty: str = "medium") -> str:
    """Generate a user instruction by randomly selecting inspiration elements."""
    if category is None:
        category = random.choice(TASK_CATEGORIES)
    context = random.choice(SCENARIO_CONTEXTS)
    difficulty_hint = DIFFICULTY_GUIDANCE.get(difficulty, DIFFICULTY_GUIDANCE["medium"])

    return (
        f"Domain: {category}. "
        f"The person writing this is a {context}. "
        f"Difficulty: {difficulty}. {difficulty_hint}"
    )



def generate_templates_batch(
    batch_size: int,
    *,
    model: str = "qwen/Qwen2.5-3B-Instruct",
    temperature: float = 1.0,
    max_tokens: int = 2048,
    max_concurrency: int = 128,
    categories: Optional[list[str]] = None,
    difficulties: Optional[list[str]] = None,
) -> list[dict]:
    """Generate multiple task templates in one batched LLM call set.

    Returns a list of dicts with keys ``description``, ``truth``, and ``difficulty``.
    Any failed requests are skipped.
    """
    if categories is None:
        categories = [None] * batch_size
    if difficulties is None:
        difficulties = ["medium"] * batch_size

    messages: list[list[dict[str, str]]] = []
    for cat, diff in zip(categories, difficulties):
        user_msg = random_user_msg(category=cat, difficulty=diff)
        messages.append([
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": user_msg},
        ])

    responses = chat_completion_batch(
        messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        num_completions=1,
        max_concurrency=max_concurrency,
    )

    results: list[dict] = []
    for idx, resp in enumerate(responses):
        if resp is None:
            continue
        try:
            content = resp.choices[0].message.content.strip()
            parsed = parse_template(content)
            parsed["difficulty"] = difficulties[idx]
            results.append(parsed)
        except Exception:
            # Skip malformed entries
            continue

    return results

def parse_template(raw: str) -> dict:
    """Convert the raw XML *raw* into a structured ``dict``."""

    # Extract the task description template
    template = re.search(r"<task>(.*?)</task>", raw, re.DOTALL).group(1).strip()
    if not template:
        raise ValueError("No task description found in the response.")

    # Extract ground-truth section (optional)
    truth_data = re.search(r"<truth>(.*?)</truth>", raw, re.DOTALL).group(1).strip()
    if not truth_data:
        raise ValueError("No truth data found in the response.")

    return {"description": template, "truth": truth_data}


if __name__ == "__main__":


    tasks = generate_templates_batch(
        batch_size=100,
        model="qwen/qwen-3-32b",
        temperature=1.0,
        max_tokens=2048,
        max_concurrency=64,
    )
    # save the tasks to a file
    for task in tasks:
        task_name = str(uuid.uuid4())
        task_path = Path("tasks") / task_name
        task_path.mkdir(parents=True, exist_ok=True)
        with open(task_path / "task.json", "w") as f:
            json.dump(task, f, indent=4)
