# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the debugging task for the diagnostics Makefile issue.
"""

import os
import subprocess
import pytest

BASE_DIR = "/home/user/diagnostics"
SRC_DIR = os.path.join(BASE_DIR, "src")
OUT_DIR = os.path.join(BASE_DIR, "out")


class TestDirectoryStructure:
    """Verify the required directory structure exists."""

    def test_diagnostics_directory_exists(self):
        assert os.path.isdir(BASE_DIR), f"Directory {BASE_DIR} does not exist"

    def test_src_directory_exists(self):
        assert os.path.isdir(SRC_DIR), f"Directory {SRC_DIR} does not exist"

    def test_out_directory_exists(self):
        assert os.path.isdir(OUT_DIR), f"Directory {OUT_DIR} does not exist"


class TestRequiredFiles:
    """Verify all required source files exist."""

    def test_makefile_exists(self):
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        assert os.path.isfile(makefile_path), f"Makefile not found at {makefile_path}"

    def test_sysinfo_script_exists(self):
        script_path = os.path.join(SRC_DIR, "sysinfo.sh")
        assert os.path.isfile(script_path), f"sysinfo.sh not found at {script_path}"

    def test_netstat_parser_exists(self):
        script_path = os.path.join(SRC_DIR, "netstat_parser.py")
        assert os.path.isfile(script_path), f"netstat_parser.py not found at {script_path}"

    def test_diskcheck_script_exists(self):
        script_path = os.path.join(SRC_DIR, "diskcheck.sh")
        assert os.path.isfile(script_path), f"diskcheck.sh not found at {script_path}"

    def test_combine_script_exists(self):
        script_path = os.path.join(SRC_DIR, "combine.py")
        assert os.path.isfile(script_path), f"combine.py not found at {script_path}"

    def test_env_file_exists(self):
        env_path = os.path.join(BASE_DIR, ".env")
        assert os.path.isfile(env_path), f".env file not found at {env_path}"


class TestMakefileStructure:
    """Verify Makefile has the expected targets."""

    def test_makefile_has_collect_target(self):
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        with open(makefile_path, 'r') as f:
            content = f.read()
        assert "collect:" in content or "collect :" in content, \
            "Makefile missing 'collect' target"

    def test_makefile_has_clean_target(self):
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        with open(makefile_path, 'r') as f:
            content = f.read()
        assert "clean:" in content or "clean :" in content, \
            "Makefile missing 'clean' target"

    def test_makefile_has_report_txt_target(self):
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        with open(makefile_path, 'r') as f:
            content = f.read()
        assert "out/report.txt:" in content or "out/report.txt :" in content, \
            "Makefile missing 'out/report.txt' target"

    def test_makefile_invokes_combine_py(self):
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        with open(makefile_path, 'r') as f:
            content = f.read()
        assert "combine.py" in content, \
            "Makefile should invoke combine.py for generating report"


class TestBug1NetstatParser:
    """Verify Bug 1 conditions exist - netstat_parser.py has the problematic os.chdir."""

    def test_netstat_parser_has_chdir_to_tmp(self):
        script_path = os.path.join(SRC_DIR, "netstat_parser.py")
        with open(script_path, 'r') as f:
            content = f.read()
        assert "os.chdir" in content and "/tmp" in content, \
            "Bug 1 setup: netstat_parser.py should have os.chdir('/tmp') leftover debug code"


class TestBug2DiskcheckScript:
    """Verify Bug 2 conditions exist - diskcheck.sh has malformed default assignment."""

    def test_diskcheck_sources_env_file(self):
        script_path = os.path.join(SRC_DIR, "diskcheck.sh")
        with open(script_path, 'r') as f:
            content = f.read()
        assert "source" in content and ".env" in content, \
            "Bug 2 setup: diskcheck.sh should source the .env file"

    def test_diskcheck_has_malformed_default(self):
        script_path = os.path.join(SRC_DIR, "diskcheck.sh")
        with open(script_path, 'r') as f:
            content = f.read()
        # Should have ${VAR-default} instead of ${VAR:-default}
        # The malformed version is missing the colon
        assert "DIAG_DISK_TARGET-" in content or "${DIAG_DISK_TARGET-" in content, \
            "Bug 2 setup: diskcheck.sh should have malformed default assignment (missing colon)"


class TestEnvFile:
    """Verify .env file has the problematic empty DIAG_DISK_TARGET."""

    def test_env_file_has_empty_disk_target(self):
        env_path = os.path.join(BASE_DIR, ".env")
        with open(env_path, 'r') as f:
            content = f.read()
        # Should have DIAG_DISK_TARGET="" or DIAG_DISK_TARGET=
        assert 'DIAG_DISK_TARGET=""' in content or 'DIAG_DISK_TARGET=' in content, \
            "Bug 2 setup: .env should set DIAG_DISK_TARGET to empty string"


class TestFilePermissions:
    """Verify files are writable by user."""

    def test_makefile_is_writable(self):
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        assert os.access(makefile_path, os.W_OK), f"Makefile at {makefile_path} is not writable"

    def test_netstat_parser_is_writable(self):
        script_path = os.path.join(SRC_DIR, "netstat_parser.py")
        assert os.access(script_path, os.W_OK), f"netstat_parser.py at {script_path} is not writable"

    def test_diskcheck_is_writable(self):
        script_path = os.path.join(SRC_DIR, "diskcheck.sh")
        assert os.access(script_path, os.W_OK), f"diskcheck.sh at {script_path} is not writable"

    def test_combine_is_writable(self):
        script_path = os.path.join(SRC_DIR, "combine.py")
        assert os.access(script_path, os.W_OK), f"combine.py at {script_path} is not writable"

    def test_env_file_is_writable(self):
        env_path = os.path.join(BASE_DIR, ".env")
        assert os.access(env_path, os.W_OK), f".env at {env_path} is not writable"

    def test_out_directory_is_writable(self):
        assert os.access(OUT_DIR, os.W_OK), f"out/ directory at {OUT_DIR} is not writable"


class TestRequiredTools:
    """Verify required system tools are available."""

    def test_python3_available(self):
        result = subprocess.run(["which", "python3"], capture_output=True)
        assert result.returncode == 0, "python3 is not available in PATH"

    def test_bash_available(self):
        result = subprocess.run(["which", "bash"], capture_output=True)
        assert result.returncode == 0, "bash is not available in PATH"

    def test_make_available(self):
        result = subprocess.run(["which", "make"], capture_output=True)
        assert result.returncode == 0, "make is not available in PATH"

    def test_ss_available(self):
        result = subprocess.run(["which", "ss"], capture_output=True)
        assert result.returncode == 0, "ss is not available in PATH"

    def test_df_available(self):
        result = subprocess.run(["which", "df"], capture_output=True)
        assert result.returncode == 0, "df is not available in PATH"


class TestCombineScript:
    """Verify combine.py has expected structure."""

    def test_combine_reads_from_out_directory(self):
        script_path = os.path.join(SRC_DIR, "combine.py")
        with open(script_path, 'r') as f:
            content = f.read()
        assert "out/" in content or "out\\" in content or "'out'" in content or '"out"' in content, \
            "combine.py should read from out/ directory"

    def test_combine_writes_report_txt(self):
        script_path = os.path.join(SRC_DIR, "combine.py")
        with open(script_path, 'r') as f:
            content = f.read()
        assert "report.txt" in content, \
            "combine.py should write to report.txt"


class TestMakeCollectFails:
    """Verify that make collect currently fails (the bug exists)."""

    def test_make_collect_fails_initially(self):
        # First clean any existing state
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True)

        # Now try to run make collect - it should fail
        result = subprocess.run(
            ["make", "collect"],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=30
        )

        # The task states that make collect is "dying partway through"
        # So either it returns non-zero, or the report is incomplete
        report_path = os.path.join(OUT_DIR, "report.txt")

        if result.returncode == 0 and os.path.isfile(report_path):
            # If it somehow succeeded, check if report is complete
            with open(report_path, 'r') as f:
                content = f.read()
            # Check for all required sections
            has_all_sections = (
                "=== SYSTEM INFO ===" in content and
                "=== NETWORK ===" in content and
                "=== DISK ===" in content
            )
            assert not has_all_sections, \
                "Bug not present: make collect should fail or produce incomplete report initially"
        else:
            # Expected: make collect fails
            assert result.returncode != 0 or not os.path.isfile(report_path), \
                "Initial state verified: make collect fails as expected"
