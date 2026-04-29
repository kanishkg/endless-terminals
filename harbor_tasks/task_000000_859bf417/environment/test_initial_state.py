# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student
attempts to fix the firewall rules script.
"""

import os
import stat
import subprocess
import pytest


HOME = "/home/user"
FIREWALL_DIR = os.path.join(HOME, "firewall")
RULES_SCRIPT = os.path.join(FIREWALL_DIR, "rules.sh")
TEST_FRONTEND_TO_API = os.path.join(FIREWALL_DIR, "test_frontend_to_api.sh")
TEST_API_TO_POSTGRES = os.path.join(FIREWALL_DIR, "test_api_to_postgres.sh")
TEST_ALL = os.path.join(FIREWALL_DIR, "test_all.sh")


class TestFirewallDirectoryExists:
    """Test that the firewall directory exists and is writable."""

    def test_firewall_directory_exists(self):
        """The /home/user/firewall/ directory must exist."""
        assert os.path.isdir(FIREWALL_DIR), (
            f"Directory {FIREWALL_DIR} does not exist. "
            "The firewall directory must be present for the task."
        )

    def test_firewall_directory_is_writable(self):
        """The /home/user/firewall/ directory must be writable."""
        assert os.access(FIREWALL_DIR, os.W_OK), (
            f"Directory {FIREWALL_DIR} is not writable. "
            "The student needs write access to modify the rules script."
        )


class TestRulesScriptExists:
    """Test that the rules.sh script exists with expected properties."""

    def test_rules_script_exists(self):
        """The rules.sh script must exist."""
        assert os.path.isfile(RULES_SCRIPT), (
            f"File {RULES_SCRIPT} does not exist. "
            "The firewall rules script must be present for the task."
        )

    def test_rules_script_is_executable(self):
        """The rules.sh script must be executable."""
        assert os.access(RULES_SCRIPT, os.X_OK), (
            f"File {RULES_SCRIPT} is not executable. "
            "The script should have execute permissions."
        )

    def test_rules_script_is_bash_script(self):
        """The rules.sh script must be a bash script."""
        with open(RULES_SCRIPT, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == "#!/bin/bash", (
            f"File {RULES_SCRIPT} does not start with #!/bin/bash. "
            f"Found: {first_line}"
        )

    def test_rules_script_contains_iptables_commands(self):
        """The rules.sh script must contain iptables commands."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "iptables" in content, (
            f"File {RULES_SCRIPT} does not contain any iptables commands. "
            "The script should use iptables for firewall configuration."
        )


class TestRulesScriptHasBugs:
    """Test that the rules.sh script contains the expected bugs to fix."""

    def test_has_early_drop_rule(self):
        """The script should have an early DROP rule (bug #1)."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        # Check for the explicit DROP-all rule before ACCEPT rules
        assert "iptables -A INPUT -j DROP" in content, (
            f"File {RULES_SCRIPT} should contain 'iptables -A INPUT -j DROP' "
            "as one of the bugs to fix."
        )

    def test_has_dport_without_protocol(self):
        """The script should have --dport without -p tcp (bug #2)."""
        with open(RULES_SCRIPT, 'r') as f:
            lines = f.readlines()

        # Find lines with --dport but without -p tcp or -p udp
        dport_lines_without_protocol = []
        for line in lines:
            if "--dport" in line:
                if "-p tcp" not in line and "-p udp" not in line:
                    dport_lines_without_protocol.append(line.strip())

        assert len(dport_lines_without_protocol) > 0, (
            f"File {RULES_SCRIPT} should contain rules with --dport "
            "but without -p tcp (this is one of the bugs to fix)."
        )

    def test_has_wrong_chain_for_frontend_rule(self):
        """The script should have the frontend→API rule in OUTPUT chain (bug #3)."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        # The rule for frontend to API should incorrectly be in OUTPUT
        assert "iptables -A OUTPUT" in content and "10.0.1.10" in content, (
            f"File {RULES_SCRIPT} should contain a rule in OUTPUT chain "
            "for the frontend IP (10.0.1.10) - this is a bug to fix."
        )

    def test_has_typo_in_postgres_ip(self):
        """The script should have typo 10.0.1.130 instead of 10.0.1.30 (bug #4)."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "10.0.1.130" in content, (
            f"File {RULES_SCRIPT} should contain the typo '10.0.1.130' "
            "instead of '10.0.1.30' for the postgres destination."
        )

    def test_established_rule_comes_after_drop(self):
        """The ESTABLISHED rule should come after the DROP rule (bug #5)."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()

        drop_pos = content.find("iptables -A INPUT -j DROP")
        established_pos = content.find("ESTABLISHED,RELATED")

        assert drop_pos != -1 and established_pos != -1, (
            f"File {RULES_SCRIPT} should contain both DROP and ESTABLISHED rules."
        )
        assert drop_pos < established_pos, (
            f"File {RULES_SCRIPT} should have the DROP rule before the "
            "ESTABLISHED rule (this ordering is a bug to fix)."
        )


class TestTestScriptsExist:
    """Test that the test scripts exist and are executable."""

    def test_test_frontend_to_api_exists(self):
        """The test_frontend_to_api.sh script must exist."""
        assert os.path.isfile(TEST_FRONTEND_TO_API), (
            f"File {TEST_FRONTEND_TO_API} does not exist. "
            "This test script is needed to verify the fix."
        )

    def test_test_frontend_to_api_is_executable(self):
        """The test_frontend_to_api.sh script must be executable."""
        assert os.access(TEST_FRONTEND_TO_API, os.X_OK), (
            f"File {TEST_FRONTEND_TO_API} is not executable."
        )

    def test_test_api_to_postgres_exists(self):
        """The test_api_to_postgres.sh script must exist."""
        assert os.path.isfile(TEST_API_TO_POSTGRES), (
            f"File {TEST_API_TO_POSTGRES} does not exist. "
            "This test script is needed to verify the fix."
        )

    def test_test_api_to_postgres_is_executable(self):
        """The test_api_to_postgres.sh script must be executable."""
        assert os.access(TEST_API_TO_POSTGRES, os.X_OK), (
            f"File {TEST_API_TO_POSTGRES} is not executable."
        )

    def test_test_all_exists(self):
        """The test_all.sh script must exist."""
        assert os.path.isfile(TEST_ALL), (
            f"File {TEST_ALL} does not exist. "
            "This test script is needed to verify the complete fix."
        )

    def test_test_all_is_executable(self):
        """The test_all.sh script must be executable."""
        assert os.access(TEST_ALL, os.X_OK), (
            f"File {TEST_ALL} is not executable."
        )


class TestIptablesAvailable:
    """Test that iptables command is available."""

    def test_iptables_command_exists(self):
        """The iptables command must be available."""
        result = subprocess.run(
            ["which", "iptables"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "The 'iptables' command is not available in PATH. "
            "It is required for this task."
        )


class TestRequiredTools:
    """Test that required tools are available."""

    def test_bash_available(self):
        """Bash must be available."""
        result = subprocess.run(["which", "bash"], capture_output=True, text=True)
        assert result.returncode == 0, "bash is not available"

    def test_python3_available(self):
        """Python3 must be available."""
        result = subprocess.run(["which", "python3"], capture_output=True, text=True)
        assert result.returncode == 0, "python3 is not available"

    def test_grep_available(self):
        """grep must be available."""
        result = subprocess.run(["which", "grep"], capture_output=True, text=True)
        assert result.returncode == 0, "grep is not available"

    def test_sed_available(self):
        """sed must be available."""
        result = subprocess.run(["which", "sed"], capture_output=True, text=True)
        assert result.returncode == 0, "sed is not available"

    def test_awk_available(self):
        """awk must be available."""
        result = subprocess.run(["which", "awk"], capture_output=True, text=True)
        assert result.returncode == 0, "awk is not available"


class TestExpectedNetworkConfiguration:
    """Test that the script references the expected network configuration."""

    def test_references_frontend_ip(self):
        """The script should reference the frontend IP 10.0.1.10."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "10.0.1.10" in content, (
            f"File {RULES_SCRIPT} should reference frontend IP 10.0.1.10"
        )

    def test_references_api_ip(self):
        """The script should reference the API IP 10.0.1.20."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "10.0.1.20" in content, (
            f"File {RULES_SCRIPT} should reference API IP 10.0.1.20"
        )

    def test_references_port_8080(self):
        """The script should reference port 8080 for the API."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "8080" in content, (
            f"File {RULES_SCRIPT} should reference port 8080 for the API"
        )

    def test_references_port_5432(self):
        """The script should reference port 5432 for postgres."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "5432" in content, (
            f"File {RULES_SCRIPT} should reference port 5432 for postgres"
        )

    def test_has_drop_policy_for_input(self):
        """The script should set DROP policy for INPUT chain."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "iptables -P INPUT DROP" in content, (
            f"File {RULES_SCRIPT} should have 'iptables -P INPUT DROP' "
            "for security (this policy should be maintained in the fix)"
        )

    def test_has_localhost_rule(self):
        """The script should have a localhost rule."""
        with open(RULES_SCRIPT, 'r') as f:
            content = f.read()
        assert "-i lo" in content or "localhost" in content.lower(), (
            f"File {RULES_SCRIPT} should have a rule for localhost traffic"
        )
