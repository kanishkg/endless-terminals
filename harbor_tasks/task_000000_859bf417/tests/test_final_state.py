# test_final_state.py
"""
Tests to validate the final state after the student has fixed the firewall rules script.
These tests verify that:
1. The rules.sh script runs successfully
2. The test_all.sh validation passes
3. The firewall rules correctly allow required traffic
4. Security policies are maintained
"""

import os
import subprocess
import pytest
import re


HOME = "/home/user"
FIREWALL_DIR = os.path.join(HOME, "firewall")
RULES_SCRIPT = os.path.join(FIREWALL_DIR, "rules.sh")
TEST_FRONTEND_TO_API = os.path.join(FIREWALL_DIR, "test_frontend_to_api.sh")
TEST_API_TO_POSTGRES = os.path.join(FIREWALL_DIR, "test_api_to_postgres.sh")
TEST_ALL = os.path.join(FIREWALL_DIR, "test_all.sh")
IPTABLES_STATE = "/tmp/iptables_state.txt"


class TestRulesScriptExecution:
    """Test that the rules.sh script executes successfully."""

    def test_rules_script_exists(self):
        """The rules.sh script must still exist."""
        assert os.path.isfile(RULES_SCRIPT), (
            f"File {RULES_SCRIPT} does not exist. "
            "The firewall rules script must be present."
        )

    def test_rules_script_is_executable(self):
        """The rules.sh script must be executable."""
        assert os.access(RULES_SCRIPT, os.X_OK), (
            f"File {RULES_SCRIPT} is not executable. "
            "The script should have execute permissions."
        )

    def test_rules_script_is_bash_script(self):
        """The rules.sh script must still be a bash script."""
        with open(RULES_SCRIPT, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == "#!/bin/bash", (
            f"File {RULES_SCRIPT} must start with #!/bin/bash. "
            f"Found: {first_line}. The script must remain a bash script."
        )

    def test_rules_script_contains_iptables_commands(self):
        """The rules.sh script must contain iptables commands (not a stub)."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        # Count iptables commands to ensure it's not a trivial stub
        iptables_count = content.count("iptables")
        assert iptables_count >= 5, (
            f"File {RULES_SCRIPT} should contain multiple iptables commands. "
            f"Found only {iptables_count}. The script must use iptables for firewall configuration."
        )

    def test_rules_script_runs_successfully(self):
        """Running rules.sh must exit with code 0."""
        result = subprocess.run(
            ["bash", RULES_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"Running {RULES_SCRIPT} failed with exit code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


class TestConnectivityValidation:
    """Test that the connectivity tests pass after running rules.sh."""

    @pytest.fixture(autouse=True)
    def run_rules_script(self):
        """Run the rules script before each test in this class."""
        result = subprocess.run(
            ["bash", RULES_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Don't fail here, let individual tests report the issue
        yield result

    def test_test_all_passes(self):
        """Running test_all.sh after rules.sh must exit with code 0."""
        # First run rules.sh
        rules_result = subprocess.run(
            ["bash", RULES_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert rules_result.returncode == 0, (
            f"rules.sh failed: {rules_result.stderr}"
        )

        # Then run test_all.sh
        result = subprocess.run(
            ["bash", TEST_ALL],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"Running {TEST_ALL} failed with exit code {result.returncode}.\n"
            f"This means the firewall rules are not correctly configured.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_frontend_to_api_passes(self):
        """Frontend (10.0.1.10) must be able to reach API (10.0.1.20:8080)."""
        # First run rules.sh
        subprocess.run(["bash", RULES_SCRIPT], capture_output=True, timeout=30)

        result = subprocess.run(
            ["bash", TEST_FRONTEND_TO_API],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"Frontend to API connectivity test failed.\n"
            f"TCP packets from 10.0.1.10 to 10.0.1.20:8080 should be accepted.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_api_to_postgres_passes(self):
        """API (10.0.1.20) must be able to reach Postgres (10.0.1.30:5432)."""
        # First run rules.sh
        subprocess.run(["bash", RULES_SCRIPT], capture_output=True, timeout=30)

        result = subprocess.run(
            ["bash", TEST_API_TO_POSTGRES],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"API to Postgres connectivity test failed.\n"
            f"TCP packets from 10.0.1.20 to 10.0.1.30:5432 should be accepted.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


class TestSecurityPoliciesMaintained:
    """Test that security policies are maintained in the fixed script."""

    def test_input_policy_is_drop(self):
        """Default INPUT policy must remain DROP for security."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "iptables -P INPUT DROP" in content, (
            f"File {RULES_SCRIPT} must maintain 'iptables -P INPUT DROP' "
            "for security. The default INPUT policy must be DROP."
        )

    def test_output_policy_is_accept(self):
        """Default OUTPUT policy must remain ACCEPT."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "iptables -P OUTPUT ACCEPT" in content, (
            f"File {RULES_SCRIPT} must maintain 'iptables -P OUTPUT ACCEPT'."
        )

    def test_localhost_rule_exists(self):
        """Localhost traffic must still be allowed."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        # Check for localhost rule (either -i lo or 127.0.0.1)
        has_lo_interface = "-i lo" in content
        has_localhost_ip = "127.0.0.1" in content
        assert has_lo_interface or has_localhost_ip, (
            f"File {RULES_SCRIPT} must have a rule allowing localhost traffic "
            "(either '-i lo' or '127.0.0.1')."
        )


class TestBugsFixed:
    """Test that the specific bugs have been fixed."""

    def test_no_early_drop_all_rule(self):
        """The early 'iptables -A INPUT -j DROP' rule must be removed or moved."""
        with open(RULES_SCRIPT, 'r') as f:
            lines = f.readlines()

        # Find positions of relevant rules
        drop_all_positions = []
        accept_rule_positions = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Skip comments
            if line_stripped.startswith('#'):
                continue
            # Check for DROP all rule
            if re.search(r'iptables\s+-A\s+INPUT\s+-j\s+DROP', line_stripped):
                drop_all_positions.append(i)
            # Check for ACCEPT rules in INPUT chain
            if re.search(r'iptables\s+-A\s+INPUT\s+.*-j\s+ACCEPT', line_stripped):
                accept_rule_positions.append(i)

        # If there's a DROP all rule, it must come AFTER all ACCEPT rules
        if drop_all_positions and accept_rule_positions:
            first_drop = min(drop_all_positions)
            last_accept = max(accept_rule_positions)
            assert first_drop > last_accept, (
                f"The 'iptables -A INPUT -j DROP' rule at line {first_drop + 1} "
                f"comes before ACCEPT rules (last at line {last_accept + 1}). "
                "This blocks all traffic before the ACCEPT rules can match. "
                "Either remove the explicit DROP rule (policy handles it) or move it to the end."
            )

    def test_dport_rules_have_protocol(self):
        """All rules using --dport must specify -p tcp or -p udp."""
        with open(RULES_SCRIPT, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if "--dport" in line:
                has_protocol = "-p tcp" in line or "-p udp" in line
                assert has_protocol, (
                    f"Line {i + 1} uses --dport without specifying protocol:\n"
                    f"  {line.strip()}\n"
                    "Rules with --dport must include '-p tcp' or '-p udp'."
                )

    def test_frontend_rule_in_correct_chain(self):
        """The frontend→API rule must be in INPUT chain, not OUTPUT."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()

        # Check that there's no rule in OUTPUT for frontend to API
        # The rule should allow traffic TO the API, which means INPUT on the API
        output_frontend_pattern = re.search(
            r'iptables\s+-A\s+OUTPUT\s+.*10\.0\.1\.10.*10\.0\.1\.20.*8080',
            content
        )
        assert output_frontend_pattern is None, (
            "Found frontend→API rule in OUTPUT chain. "
            "This rule should be in the INPUT chain (traffic arriving at the API)."
        )

        # Verify there's a proper INPUT rule for this traffic
        input_frontend_pattern = re.search(
            r'iptables\s+-A\s+INPUT\s+.*-s\s+10\.0\.1\.10.*-d\s+10\.0\.1\.20.*--dport\s+8080',
            content
        ) or re.search(
            r'iptables\s+-A\s+INPUT\s+.*10\.0\.1\.10.*8080',
            content
        )
        # This is checked by the connectivity tests, so just a soft check here

    def test_postgres_ip_is_correct(self):
        """The postgres destination IP must be 10.0.1.30, not 10.0.1.130."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()

        # Check for the typo
        assert "10.0.1.130" not in content, (
            "Found typo '10.0.1.130' in the script. "
            "The postgres IP should be '10.0.1.30'."
        )

        # Check for correct IP in postgres-related rule
        assert "10.0.1.30" in content, (
            "The correct postgres IP '10.0.1.30' is not found in the script. "
            "The API→Postgres rule needs the correct destination IP."
        )

    def test_established_related_rule_effective(self):
        """The ESTABLISHED,RELATED rule must be in a position where it works."""
        with open(RULES_SCRIPT, 'r') as f:
            lines = f.readlines()

        established_pos = None
        drop_all_pos = None

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                continue
            if "ESTABLISHED" in line and "RELATED" in line and "-A INPUT" in line:
                established_pos = i
            if re.search(r'iptables\s+-A\s+INPUT\s+-j\s+DROP\s*$', line_stripped):
                drop_all_pos = i

        assert established_pos is not None, (
            "No ESTABLISHED,RELATED rule found in INPUT chain. "
            "Return traffic must be allowed."
        )

        # If there's an explicit DROP all, ESTABLISHED must come before it
        if drop_all_pos is not None:
            assert established_pos < drop_all_pos, (
                f"ESTABLISHED,RELATED rule (line {established_pos + 1}) comes after "
                f"DROP all rule (line {drop_all_pos + 1}). "
                "The ESTABLISHED rule must come before any catch-all DROP."
            )


class TestRuleOrderAndStructure:
    """Test the overall structure and order of rules."""

    def test_flush_rules_at_start(self):
        """The script should flush existing rules at the start."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "iptables -F" in content, (
            "The script should flush existing rules with 'iptables -F'."
        )

    def test_policies_set_before_rules(self):
        """Policies should be set before adding rules."""
        with open(RULES_SCRIPT, 'r') as f:
            lines = f.readlines()

        policy_pos = None
        first_append_pos = None

        for i, line in enumerate(lines):
            if "iptables -P" in line and policy_pos is None:
                policy_pos = i
            if "iptables -A" in line and first_append_pos is None:
                first_append_pos = i

        if policy_pos is not None and first_append_pos is not None:
            assert policy_pos < first_append_pos, (
                "Policies (-P) should be set before appending rules (-A)."
            )


class TestFinalStateIntegration:
    """Integration tests for the complete final state."""

    def test_complete_workflow(self):
        """Test the complete workflow: run rules.sh then test_all.sh."""
        # Run rules.sh
        rules_result = subprocess.run(
            ["bash", RULES_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert rules_result.returncode == 0, (
            f"rules.sh failed with exit code {rules_result.returncode}:\n"
            f"stderr: {rules_result.stderr}"
        )

        # Run test_all.sh
        test_result = subprocess.run(
            ["bash", TEST_ALL],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert test_result.returncode == 0, (
            f"test_all.sh failed with exit code {test_result.returncode}:\n"
            f"stdout: {test_result.stdout}\n"
            f"stderr: {test_result.stderr}\n"
            "The firewall rules are not correctly configured to allow:\n"
            "  - Frontend (10.0.1.10) → API (10.0.1.20:8080)\n"
            "  - API (10.0.1.20) → Postgres (10.0.1.30:5432)"
        )

    def test_rules_script_idempotent(self):
        """Running rules.sh multiple times should produce consistent results."""
        # Run twice
        for _ in range(2):
            result = subprocess.run(
                ["bash", RULES_SCRIPT],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, (
                f"rules.sh is not idempotent - failed on repeated run:\n"
                f"stderr: {result.stderr}"
            )

        # Test should still pass
        test_result = subprocess.run(
            ["bash", TEST_ALL],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert test_result.returncode == 0, (
            "test_all.sh failed after running rules.sh multiple times. "
            "The script should be idempotent."
        )
