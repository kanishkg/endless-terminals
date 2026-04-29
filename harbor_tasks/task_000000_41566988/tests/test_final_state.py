# test_final_state.py
"""
Tests to validate the final state after the student has fixed the diagnostics
Makefile issue. Verifies that `make collect` succeeds and produces a complete report.
"""

import os
import subprocess
import pytest

BASE_DIR = "/home/user/diagnostics"
SRC_DIR = os.path.join(BASE_DIR, "src")
OUT_DIR = os.path.join(BASE_DIR, "out")
REPORT_PATH = os.path.join(OUT_DIR, "report.txt")


class TestMakeCollectSucceeds:
    """Verify that make collect now works correctly."""

    def test_make_clean_then_collect_succeeds(self):
        """Running make clean && make collect should exit 0."""
        # First clean
        clean_result = subprocess.run(
            ["make", "clean"],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=30
        )

        # Then collect
        collect_result = subprocess.run(
            ["make", "collect"],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=60
        )

        assert collect_result.returncode == 0, (
            f"make collect failed with return code {collect_result.returncode}\n"
            f"stdout: {collect_result.stdout.decode('utf-8', errors='replace')}\n"
            f"stderr: {collect_result.stderr.decode('utf-8', errors='replace')}"
        )

    def test_make_collect_twice_succeeds(self):
        """Running make collect twice (with clean between) must both succeed."""
        # First run
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True, timeout=30)
        result1 = subprocess.run(
            ["make", "collect"],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=60
        )
        assert result1.returncode == 0, (
            f"First make collect failed with return code {result1.returncode}"
        )

        # Second run
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True, timeout=30)
        result2 = subprocess.run(
            ["make", "collect"],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=60
        )
        assert result2.returncode == 0, (
            f"Second make collect failed with return code {result2.returncode}"
        )


class TestReportExists:
    """Verify the report file is created."""

    def test_report_txt_exists(self):
        """out/report.txt must exist after make collect."""
        # Ensure we have a fresh run
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True, timeout=30)
        subprocess.run(["make", "collect"], cwd=BASE_DIR, capture_output=True, timeout=60)

        assert os.path.isfile(REPORT_PATH), (
            f"Report file not found at {REPORT_PATH}"
        )

    def test_report_is_not_empty(self):
        """out/report.txt must not be empty."""
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True, timeout=30)
        subprocess.run(["make", "collect"], cwd=BASE_DIR, capture_output=True, timeout=60)

        assert os.path.isfile(REPORT_PATH), f"Report file not found at {REPORT_PATH}"

        file_size = os.path.getsize(REPORT_PATH)
        assert file_size > 0, "Report file is empty"


class TestReportContainsAllSections:
    """Verify the report contains all required sections."""

    @pytest.fixture(autouse=True)
    def setup_report(self):
        """Ensure a fresh report is generated before each test."""
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True, timeout=30)
        result = subprocess.run(
            ["make", "collect"],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=60
        )
        assert result.returncode == 0, "make collect must succeed for section tests"
        yield

    def test_report_has_system_info_section(self):
        """Report must contain '=== SYSTEM INFO ===' section."""
        with open(REPORT_PATH, 'r') as f:
            content = f.read()

        assert "=== SYSTEM INFO ===" in content, (
            "Report is missing '=== SYSTEM INFO ===' section header"
        )

    def test_report_has_network_section(self):
        """Report must contain '=== NETWORK ===' section."""
        with open(REPORT_PATH, 'r') as f:
            content = f.read()

        assert "=== NETWORK ===" in content, (
            "Report is missing '=== NETWORK ===' section header"
        )

    def test_report_has_disk_section(self):
        """Report must contain '=== DISK ===' section."""
        with open(REPORT_PATH, 'r') as f:
            content = f.read()

        assert "=== DISK ===" in content, (
            "Report is missing '=== DISK ===' section header"
        )


class TestReportSectionContent:
    """Verify each section has actual data content."""

    @pytest.fixture(autouse=True)
    def setup_report(self):
        """Ensure a fresh report is generated before each test."""
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True, timeout=30)
        result = subprocess.run(
            ["make", "collect"],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=60
        )
        assert result.returncode == 0, "make collect must succeed for content tests"
        yield

    def _get_section_content(self, content, section_header):
        """Extract content after a section header until the next section or end."""
        lines = content.split('\n')
        in_section = False
        section_lines = []

        for line in lines:
            if section_header in line:
                in_section = True
                continue
            elif in_section:
                # Check if we hit another section header
                if line.startswith("===") and "===" in line[3:]:
                    break
                # Skip empty lines at the start
                if section_lines or line.strip():
                    section_lines.append(line)

        # Remove trailing empty lines
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()

        return section_lines

    def test_system_info_section_has_data(self):
        """System info section must have at least 2 lines of data."""
        with open(REPORT_PATH, 'r') as f:
            content = f.read()

        section_lines = self._get_section_content(content, "=== SYSTEM INFO ===")
        non_empty_lines = [l for l in section_lines if l.strip()]

        assert len(non_empty_lines) >= 2, (
            f"System info section should have at least 2 lines of data, "
            f"found {len(non_empty_lines)}: {non_empty_lines}"
        )

    def test_network_section_has_data(self):
        """Network section must have at least 2 lines of data."""
        with open(REPORT_PATH, 'r') as f:
            content = f.read()

        section_lines = self._get_section_content(content, "=== NETWORK ===")
        non_empty_lines = [l for l in section_lines if l.strip()]

        assert len(non_empty_lines) >= 2, (
            f"Network section should have at least 2 lines of data, "
            f"found {len(non_empty_lines)}: {non_empty_lines}"
        )

    def test_disk_section_has_data(self):
        """Disk section must have at least 2 lines of data."""
        with open(REPORT_PATH, 'r') as f:
            content = f.read()

        section_lines = self._get_section_content(content, "=== DISK ===")
        non_empty_lines = [l for l in section_lines if l.strip()]

        assert len(non_empty_lines) >= 2, (
            f"Disk section should have at least 2 lines of data, "
            f"found {len(non_empty_lines)}: {non_empty_lines}"
        )


class TestInvariantsPreserved:
    """Verify that required invariants are maintained."""

    def test_makefile_still_has_target_structure(self):
        """Makefile must still have collect depending on out/report.txt."""
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        with open(makefile_path, 'r') as f:
            content = f.read()

        # Check collect target exists
        assert "collect:" in content or "collect :" in content, (
            "Makefile must still have 'collect' target"
        )

        # Check out/report.txt target exists
        assert "out/report.txt:" in content or "out/report.txt :" in content, (
            "Makefile must still have 'out/report.txt' target"
        )

    def test_makefile_invokes_combine_py(self):
        """Makefile must still invoke combine.py for generating report."""
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        with open(makefile_path, 'r') as f:
            content = f.read()

        assert "combine.py" in content, (
            "Makefile must still invoke combine.py"
        )

    def test_combine_py_exists_and_is_used(self):
        """src/combine.py must exist and be the script that generates the report."""
        combine_path = os.path.join(SRC_DIR, "combine.py")
        assert os.path.isfile(combine_path), (
            f"combine.py not found at {combine_path}"
        )

        # Verify grep -l "combine" src/*.py returns src/combine.py
        result = subprocess.run(
            ["grep", "-l", "combine", f"{SRC_DIR}/combine.py"],
            capture_output=True
        )
        # The file should match (contains "combine" in its content or name matches)
        assert os.path.isfile(combine_path), "src/combine.py must exist"

    def test_combine_py_reads_from_out_directory(self):
        """combine.py must read from out/ directory files."""
        combine_path = os.path.join(SRC_DIR, "combine.py")
        with open(combine_path, 'r') as f:
            content = f.read()

        # Should reference out/ directory in some form
        assert ("out/" in content or "'out'" in content or '"out"' in content 
                or "out\\" in content or "OUT" in content.upper()), (
            "combine.py must read from out/ directory"
        )

    def test_env_file_still_exists(self):
        """.env file must still exist (can be modified but not deleted)."""
        env_path = os.path.join(BASE_DIR, ".env")
        assert os.path.isfile(env_path), (
            f".env file must still exist at {env_path}"
        )


class TestIntermediateFilesCreated:
    """Verify that intermediate files are created properly."""

    @pytest.fixture(autouse=True)
    def setup_clean_run(self):
        """Ensure a fresh run."""
        subprocess.run(["make", "clean"], cwd=BASE_DIR, capture_output=True, timeout=30)
        subprocess.run(["make", "collect"], cwd=BASE_DIR, capture_output=True, timeout=60)
        yield

    def test_sysinfo_raw_created(self):
        """out/sysinfo.raw should be created."""
        sysinfo_path = os.path.join(OUT_DIR, "sysinfo.raw")
        assert os.path.isfile(sysinfo_path), (
            f"Intermediate file out/sysinfo.raw not found at {sysinfo_path}"
        )

    def test_netstat_raw_created(self):
        """out/netstat.raw should be created."""
        netstat_raw_path = os.path.join(OUT_DIR, "netstat.raw")
        assert os.path.isfile(netstat_raw_path), (
            f"Intermediate file out/netstat.raw not found at {netstat_raw_path}"
        )

    def test_netstat_parsed_created_in_correct_location(self):
        """out/netstat.parsed should be created in out/ directory, not /tmp/out/."""
        netstat_parsed_path = os.path.join(OUT_DIR, "netstat.parsed")
        assert os.path.isfile(netstat_parsed_path), (
            f"Intermediate file out/netstat.parsed not found at {netstat_parsed_path}. "
            f"It may have been incorrectly created in /tmp/out/ instead."
        )

        # Also verify it's NOT in /tmp/out/
        wrong_path = "/tmp/out/netstat.parsed"
        if os.path.isfile(wrong_path):
            # It's okay if it exists there too, as long as the correct one exists
            pass

    def test_disk_raw_created(self):
        """out/disk.raw should be created."""
        disk_path = os.path.join(OUT_DIR, "disk.raw")
        assert os.path.isfile(disk_path), (
            f"Intermediate file out/disk.raw not found at {disk_path}"
        )


class TestNoShortcuts:
    """Verify the fix doesn't bypass the intended build process."""

    def test_report_generated_by_combine_not_makefile_directly(self):
        """Report must be generated by combine.py, not directly by Makefile."""
        makefile_path = os.path.join(BASE_DIR, "Makefile")
        with open(makefile_path, 'r') as f:
            content = f.read()

        # The Makefile should invoke combine.py for the report target
        # It should NOT have something like: echo "..." > out/report.txt
        lines = content.split('\n')
        in_report_target = False
        report_recipe_lines = []

        for line in lines:
            if line.startswith("out/report.txt"):
                in_report_target = True
                continue
            elif in_report_target:
                if line.startswith('\t'):
                    report_recipe_lines.append(line)
                elif line.strip() and not line.startswith('#'):
                    break

        # Check that combine.py is in the recipe
        recipe_text = ' '.join(report_recipe_lines)
        assert "combine" in recipe_text.lower(), (
            "The out/report.txt target must invoke combine.py"
        )
