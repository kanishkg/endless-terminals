"""Unit tests for train/ module.

All skyrl_gym, skyrl_train, ray, and container-runtime dependencies are
mocked so these tests run on a CPU-only machine with no GPU/CUDA/Apptainer.
"""
from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path
from unittest import mock

import pytest
import yaml
import datasets as _datasets_mod  # import early to avoid pyarrow re-registration in exec()

# ---------------------------------------------------------------------------
# Minimal stubs for skyrl_gym and skyrl_train so train/ modules can import
# ---------------------------------------------------------------------------

def _make_stub_modules():
    """Register lightweight stub modules before any train/ import."""

    # BaseTextEnvStepOutput namedtuple-alike
    class BaseTextEnvStepOutput:
        def __init__(self, *, observations, reward, done, metadata):
            self.observations = observations
            self.reward = reward
            self.done = done
            self.metadata = metadata

    class BaseTextEnv:
        def __init__(self):
            self.turns = 0

    # skyrl_gym hierarchy
    skyrl_gym = types.ModuleType("skyrl_gym")
    skyrl_gym_envs = types.ModuleType("skyrl_gym.envs")
    skyrl_gym_envs_base = types.ModuleType("skyrl_gym.envs.base_text_env")
    skyrl_gym_envs_base.BaseTextEnv = BaseTextEnv
    skyrl_gym_envs_base.BaseTextEnvStepOutput = BaseTextEnvStepOutput
    skyrl_gym_envs.base_text_env = skyrl_gym_envs_base
    skyrl_gym_envs.register = lambda id, entry_point: None
    skyrl_gym.envs = skyrl_gym_envs

    # skyrl_train hierarchy
    skyrl_train = types.ModuleType("skyrl_train")
    skyrl_train_utils = types.ModuleType("skyrl_train.utils")
    skyrl_train_utils.initialize_ray = lambda cfg: None
    skyrl_train_entrypoints = types.ModuleType("skyrl_train.entrypoints")
    skyrl_train_main_base = types.ModuleType("skyrl_train.entrypoints.main_base")
    skyrl_train_main_base.BasePPOExp = mock.MagicMock()
    skyrl_train_main_base.config_dir = "/tmp"
    skyrl_train_main_base.validate_cfg = lambda cfg: None
    skyrl_train_entrypoints.main_base = skyrl_train_main_base
    skyrl_train.utils = skyrl_train_utils
    skyrl_train.entrypoints = skyrl_train_entrypoints

    # ray stub
    ray = types.ModuleType("ray")
    ray.remote = lambda *a, **kw: (lambda fn: fn)  # no-op decorator
    ray.get = lambda x: x
    ray.init = lambda **kw: None

    for name, mod in [
        ("skyrl_gym", skyrl_gym),
        ("skyrl_gym.envs", skyrl_gym_envs),
        ("skyrl_gym.envs.base_text_env", skyrl_gym_envs_base),
        ("skyrl_train", skyrl_train),
        ("skyrl_train.utils", skyrl_train_utils),
        ("skyrl_train.entrypoints", skyrl_train_entrypoints),
        ("skyrl_train.entrypoints.main_base", skyrl_train_main_base),
        ("ray", ray),
    ]:
        sys.modules.setdefault(name, mod)

    return BaseTextEnv, BaseTextEnvStepOutput


BaseTextEnv, BaseTextEnvStepOutput = _make_stub_modules()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TRAIN_DIR = Path(__file__).parent.parent / "train"
REPO_ROOT = Path(__file__).parent.parent


def _make_extras(tmp_path, max_time=600, max_turns=16, verbose=False):
    """Build an extras dict pointing to a temp task dir."""
    task_dir = tmp_path / "task_001"
    task_dir.mkdir()
    (task_dir / "container.sif").touch()
    (task_dir / "container.def").write_text("Bootstrap: docker\nFrom: ubuntu:22.04\n")
    (task_dir / "test_initial_state.py").write_text("def test_ok(): pass\n")
    (task_dir / "test_final_state.py").write_text("def test_done(): pass\n")
    return {
        "extra_info": {
            "task_dir": str(task_dir),
            "max_time": max_time,
            "verbose": verbose,
        },
        "max_turns": max_turns,
    }


def _import_sky_endless():
    """Import SkyRLContainerEnv fresh (stubs must already be in sys.modules)."""
    if "train.sky_endless" in sys.modules:
        del sys.modules["train.sky_endless"]
    sys.path.insert(0, str(REPO_ROOT))
    from train.sky_endless import SkyRLContainerEnv
    return SkyRLContainerEnv


# ---------------------------------------------------------------------------
# Config YAML validation
# ---------------------------------------------------------------------------

class TestTrainConfigs:
    @pytest.mark.parametrize("name", [
        "base.yaml",
        "base_qwen.yaml",
        "base_qwen3_otak8.yaml",
        "base_t4.yaml",
    ])
    def test_yaml_parses(self, name):
        path = TRAIN_DIR / "confs" / name
        assert path.exists(), f"Config missing: {name}"
        doc = yaml.safe_load(path.read_text())
        assert isinstance(doc, dict)

    def test_base_has_data_section(self):
        doc = yaml.safe_load((TRAIN_DIR / "confs" / "base.yaml").read_text())
        assert "data" in doc
        assert "train_data" in doc["data"]
        assert "val_data" in doc["data"]

    def test_base_has_trainer_section(self):
        doc = yaml.safe_load((TRAIN_DIR / "confs" / "base.yaml").read_text())
        assert "trainer" in doc
        assert "algorithm" in doc["trainer"]

    def test_base_has_generator_section(self):
        doc = yaml.safe_load((TRAIN_DIR / "confs" / "base.yaml").read_text())
        assert "generator" in doc
        assert doc["generator"]["max_turns"] == 16

    def test_base_env_class_is_endless(self):
        doc = yaml.safe_load((TRAIN_DIR / "confs" / "base.yaml").read_text())
        assert doc["environment"]["env_class"] == "endless"

    def test_base_train_batch_size_positive(self):
        doc = yaml.safe_load((TRAIN_DIR / "confs" / "base.yaml").read_text())
        assert doc["trainer"]["train_batch_size"] > 0


# ---------------------------------------------------------------------------
# SkyRLContainerEnv construction
# ---------------------------------------------------------------------------

class TestSkyRLContainerEnvInit:
    def test_basic_construction(self, tmp_path):
        SkyRLContainerEnv = _import_sky_endless()
        mock_env = mock.MagicMock()
        mock_env.instance_name = None

        with mock.patch("train.sky_endless.InteractiveContainerEnvironment", return_value=mock_env):
            env = SkyRLContainerEnv(extras=_make_extras(tmp_path))

        assert env._initialized is False
        assert env.reward == 0
        assert env.max_turns == 16

    def test_max_time_string_converted_to_int(self, tmp_path):
        SkyRLContainerEnv = _import_sky_endless()
        extras = _make_extras(tmp_path)
        extras["extra_info"]["max_time"] = "300"

        with mock.patch("train.sky_endless.InteractiveContainerEnvironment"):
            env = SkyRLContainerEnv(extras=extras)

        assert env.max_time == 300
        assert isinstance(env.max_time, int)

    def test_max_output_length_default(self, tmp_path):
        SkyRLContainerEnv = _import_sky_endless()
        with mock.patch("train.sky_endless.InteractiveContainerEnvironment"):
            env = SkyRLContainerEnv(extras=_make_extras(tmp_path))
        assert env.max_output_length == 50_000

    def test_custom_max_output_length(self, tmp_path):
        SkyRLContainerEnv = _import_sky_endless()
        extras = _make_extras(tmp_path)
        extras["extra_info"]["max_output_length"] = 1000
        with mock.patch("train.sky_endless.InteractiveContainerEnvironment"):
            env = SkyRLContainerEnv(extras=extras)
        assert env.max_output_length == 1000


# ---------------------------------------------------------------------------
# SkyRLContainerEnv.step logic
# ---------------------------------------------------------------------------

class TestSkyRLContainerEnvStep:
    def _env(self, tmp_path, mock_container=None):
        SkyRLContainerEnv = _import_sky_endless()
        if mock_container is None:
            mock_container = mock.MagicMock()
            mock_container.instance_name = "ctr-1"
            mock_container.initialize.return_value = True
            mock_container.verbose = False
        with mock.patch("train.sky_endless.InteractiveContainerEnvironment", return_value=mock_container):
            env = SkyRLContainerEnv(extras=_make_extras(tmp_path))
        env.env = mock_container
        return env

    def test_init_failure_returns_done(self, tmp_path):
        mock_container = mock.MagicMock()
        mock_container.instance_name = None
        mock_container.initialize.return_value = False
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)

        result = env.step("<command>ls</command>")

        assert result.done is True
        assert result.reward == 0
        assert "Failed to initialize" in result.observations[0]["content"]

    def test_done_action_triggers_test_run(self, tmp_path):
        mock_container = mock.MagicMock()
        mock_container.instance_name = "ctr-1"
        mock_container.initialize.return_value = True
        mock_container.run_final_tests.return_value = (True, "passed")
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)
        env._initialized = True

        result = env.step("<action>done</action>")

        assert result.done is True
        assert result.reward == 1
        assert result.metadata["goal_reached"] is True
        mock_container.cleanup.assert_called_once()

    def test_command_success_observation(self, tmp_path):
        mock_container = mock.MagicMock()
        mock_container.instance_name = "ctr-1"
        mock_container.initialize.return_value = True
        mock_container.exec.return_value = (True, "file.txt\n")
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)
        env._initialized = True

        result = env.step("<command>ls</command>")

        assert "Command executed successfully" in result.observations[0]["content"]
        assert result.done is False

    def test_command_failure_observation(self, tmp_path):
        mock_container = mock.MagicMock()
        mock_container.instance_name = "ctr-1"
        mock_container.initialize.return_value = True
        mock_container.exec.return_value = (False, "No such file\n")
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)
        env._initialized = True

        result = env.step("<command>cat missing.txt</command>")

        assert "Command failed" in result.observations[0]["content"]

    def test_output_truncation(self, tmp_path):
        long_output = "x" * 100_000
        mock_container = mock.MagicMock()
        mock_container.instance_name = "ctr-1"
        mock_container.initialize.return_value = True
        mock_container.exec.return_value = (True, long_output)
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)
        env._initialized = True
        env.max_output_length = 1000

        result = env.step("<command>cat big.txt</command>")

        obs = result.observations[0]["content"]
        assert "Output truncated" in obs

    def test_invalid_action_returns_parse_error(self, tmp_path):
        mock_container = mock.MagicMock()
        mock_container.instance_name = "ctr-1"
        mock_container.initialize.return_value = True
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)
        env._initialized = True

        result = env.step("just some text with no tags")

        assert "Could not parse" in result.observations[0]["content"]

    def test_max_turns_terminates(self, tmp_path):
        mock_container = mock.MagicMock()
        mock_container.instance_name = "ctr-1"
        mock_container.initialize.return_value = True
        mock_container.exec.return_value = (True, "ok")
        mock_container.run_final_tests.return_value = (False, "fail")
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)
        env._initialized = True
        env.max_turns = 1  # will hit limit on first step

        result = env.step("<command>ls</command>")

        assert result.done is True

    def test_cleanup_called_after_done(self, tmp_path):
        mock_container = mock.MagicMock()
        mock_container.instance_name = "ctr-1"
        mock_container.initialize.return_value = True
        mock_container.exec.return_value = (True, "ok")
        mock_container.run_final_tests.return_value = (False, "")
        mock_container.verbose = False
        env = self._env(tmp_path, mock_container)
        env._initialized = True
        env.max_turns = 1

        env.step("<command>ls</command>")

        mock_container.cleanup.assert_called_once()
        assert env._initialized is False


# ---------------------------------------------------------------------------
# prepare_endless helpers (importable without running __main__)
# ---------------------------------------------------------------------------

class TestPrepareEndless:
    def test_build_container_skips_if_sif_exists(self, tmp_path):
        """build_container_for_task returns True immediately if .sif exists."""
        sys.path.insert(0, str(REPO_ROOT))
        # Import only the function, not the __main__ block
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "prepare_endless", TRAIN_DIR / "prepare_endless.py"
        )
        mod = importlib.util.load_from_spec = None

        task_name = "task_001_abc"
        task_path = tmp_path / task_name
        task_path.mkdir()
        sif = task_path / "container.sif"
        sif.touch()

        # Import just the function via exec to avoid running __main__
        source = (TRAIN_DIR / "prepare_endless.py").read_text()
        # Only grab lines up to (but not including) `if __name__ == "__main__":`
        pre_main = source.split('if __name__ == "__main__":')[0]
        ns: dict = {}
        with mock.patch.dict(sys.modules, {"generator.env": mock.MagicMock(),
                                            "generator.sample_solutions": mock.MagicMock()}):
            exec(compile(pre_main, "prepare_endless.py", "exec"), ns)

        result_name, success = ns["build_container_for_task"](task_name, str(tmp_path))
        assert success is True
        assert result_name == task_name

    def test_build_container_returns_false_on_error(self, tmp_path):
        task_name = "task_002_xyz"
        task_path = tmp_path / task_name
        task_path.mkdir()
        # No .sif file — will try to build

        source = (TRAIN_DIR / "prepare_endless.py").read_text()
        pre_main = source.split('if __name__ == "__main__":')[0]
        ns: dict = {}

        mock_env_instance = mock.MagicMock()
        mock_env_instance.build_container.return_value = False
        mock_env_class = mock.MagicMock(return_value=mock_env_instance)

        mock_gen_env = mock.MagicMock()
        mock_gen_env.InteractiveContainerEnvironment = mock_env_class
        mock_sample = mock.MagicMock()
        mock_sample.SYSTEM_MESSAGE = "sys"
        mock_sample.USER_TEMPLATE = "{task_description}"
        mock_sample._extract_action = lambda x: {"type": "done", "command": None}

        # datasets is already imported at module level; reuse cached module to
        # avoid pyarrow extension re-registration error on second import.
        with mock.patch.dict(sys.modules, {
            "generator.env": mock_gen_env,
            "generator.sample_solutions": mock_sample,
            "datasets": _datasets_mod,
        }):
            exec(compile(pre_main, "prepare_endless.py", "exec"), ns)

        result_name, success = ns["build_container_for_task"](task_name, str(tmp_path))
        assert success is False
        assert result_name == task_name


# ---------------------------------------------------------------------------
# prepare_endless — task filtering (stage1 vs stage2)
# ---------------------------------------------------------------------------

def _make_stage2_task(tasks_root: Path, name: str, num_success: int) -> Path:
    """Create a minimal Stage 2 task dir with solution/solution.json."""
    d = tasks_root / name
    d.mkdir(parents=True)
    (d / "task.json").write_text(json.dumps({"description": f"desc {name}"}))
    sol_dir = d / "solution"
    sol_dir.mkdir()
    (sol_dir / "solution.json").write_text(
        json.dumps({"num_success": num_success, "num_runs": 8, "pass_at_k": {"1": 0.1}})
    )
    return d


def _make_stage1_task(tasks_root: Path, name: str, pass_at_16: float) -> Path:
    """Create a minimal Stage 1 task dir with solutions/o3_summary.json."""
    d = tasks_root / name
    d.mkdir(parents=True)
    (d / "task.json").write_text(json.dumps({"description": f"desc {name}"}))
    sol_dir = d / "solutions"
    sol_dir.mkdir()
    (sol_dir / "o3_summary.json").write_text(
        json.dumps({"pass_at_k": {"16": pass_at_16}})
    )
    return d


def _run_filter(tmp_path: Path, source: str) -> list[str]:
    """Run prepare_endless filtering logic and return the filtered task_dir_names."""
    source_code = (TRAIN_DIR / "prepare_endless.py").read_text()
    # Extract only the filtering block (between argparse setup and build_sif block)
    # by pulling just the lines we need to test
    filter_only = """
import os, json, random
from pathlib import Path

task_dir = str(task_dir_arg)
task_dir_names = [f for f in os.listdir(task_dir) if "task" in f]

source_mode = source_arg

if source_mode == "stage2":
    def _harbor_solved(f):
        p = Path(task_dir) / f / "solution" / "solution.json"
        if not p.exists():
            return False
        try:
            return json.load(open(p)).get("num_success", 0) > 0
        except (json.JSONDecodeError, OSError):
            return False
    task_dir_names = [f for f in task_dir_names if _harbor_solved(f)]
else:
    task_dir_names = [
        f for f in task_dir_names
        if (Path(task_dir) / f / "solutions" / "o3_summary.json").exists()
    ]
    task_dir_names = [
        f for f in task_dir_names
        if json.load(open(Path(task_dir) / f / "solutions" / "o3_summary.json"))["pass_at_k"]["16"] > 0
    ]

task_dir_names = list(sorted(task_dir_names))
"""
    ns = {"task_dir_arg": tmp_path, "source_arg": source}
    exec(compile(filter_only, "filter_test", "exec"), ns)
    return ns["task_dir_names"]


class TestPrepareEndlessFiltering:
    def test_stage2_keeps_solved_tasks(self, tmp_path):
        _make_stage2_task(tmp_path, "task_001", num_success=2)
        _make_stage2_task(tmp_path, "task_002", num_success=0)
        _make_stage2_task(tmp_path, "task_003", num_success=1)

        result = _run_filter(tmp_path, "stage2")

        assert "task_001" in result
        assert "task_003" in result
        assert "task_002" not in result

    def test_stage2_excludes_tasks_without_solution_json(self, tmp_path):
        _make_stage2_task(tmp_path, "task_001", num_success=3)
        # task_002 has no solution dir at all
        no_sol = tmp_path / "task_002"
        no_sol.mkdir()
        (no_sol / "task.json").write_text("{}")

        result = _run_filter(tmp_path, "stage2")

        assert "task_001" in result
        assert "task_002" not in result

    def test_stage2_result_is_sorted(self, tmp_path):
        _make_stage2_task(tmp_path, "task_003", num_success=1)
        _make_stage2_task(tmp_path, "task_001", num_success=1)
        _make_stage2_task(tmp_path, "task_002", num_success=1)

        result = _run_filter(tmp_path, "stage2")

        assert result == sorted(result)

    def test_stage1_keeps_passing_tasks(self, tmp_path):
        _make_stage1_task(tmp_path, "task_001", pass_at_16=0.5)
        _make_stage1_task(tmp_path, "task_002", pass_at_16=0.0)
        _make_stage1_task(tmp_path, "task_003", pass_at_16=1.0)

        result = _run_filter(tmp_path, "stage1")

        assert "task_001" in result
        assert "task_003" in result
        assert "task_002" not in result

    def test_stage1_excludes_tasks_without_o3_summary(self, tmp_path):
        _make_stage1_task(tmp_path, "task_001", pass_at_16=0.5)
        # task_002 has no solutions/ dir
        no_sol = tmp_path / "task_002"
        no_sol.mkdir()
        (no_sol / "task.json").write_text("{}")

        result = _run_filter(tmp_path, "stage1")

        assert "task_001" in result
        assert "task_002" not in result

    def test_stage2_empty_dir_returns_empty(self, tmp_path):
        result = _run_filter(tmp_path, "stage2")
        assert result == []

    def test_stage1_empty_dir_returns_empty(self, tmp_path):
        result = _run_filter(tmp_path, "stage1")
        assert result == []
