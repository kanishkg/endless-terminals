# test_final_state.py
"""
Tests to validate the final state after the student fixes the Redis configuration.
"""

import os
import subprocess
import time
import pytest


REDIS_CONFIG_PATH = "/home/user/services/redis/redis.conf"
VALID_EVICTION_POLICIES = [
    "noeviction",
    "allkeys-lru",
    "volatile-lru",
    "allkeys-random",
    "volatile-random",
    "volatile-ttl",
    "allkeys-lfu",
    "volatile-lfu",
]


class TestRedisConfigFixed:
    """Test that the Redis configuration file has been fixed with a valid policy."""

    def test_redis_config_file_still_exists(self):
        """Verify redis.conf still exists after the fix."""
        assert os.path.isfile(REDIS_CONFIG_PATH), (
            f"Redis config file does not exist at {REDIS_CONFIG_PATH}. "
            "The file should still be present after the fix."
        )

    def test_maxmemory_policy_line_exists(self):
        """Verify the maxmemory-policy line exists in the config."""
        result = subprocess.run(
            ["grep", "-E", "^maxmemory-policy", REDIS_CONFIG_PATH],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "No 'maxmemory-policy' line found in redis.conf. "
            "The config should have a maxmemory-policy directive."
        )

    def test_maxmemory_policy_is_valid(self):
        """Verify the maxmemory-policy is set to a valid eviction policy."""
        result = subprocess.run(
            ["grep", "-E", "^maxmemory-policy", REDIS_CONFIG_PATH],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "No 'maxmemory-policy' line found in redis.conf."
        )

        policy_line = result.stdout.strip()
        # Extract the policy value from the line
        parts = policy_line.split()
        assert len(parts) >= 2, (
            f"Invalid maxmemory-policy line format: '{policy_line}'. "
            "Expected format: 'maxmemory-policy <policy>'"
        )

        policy_value = parts[1]
        assert policy_value in VALID_EVICTION_POLICIES, (
            f"Invalid maxmemory-policy value: '{policy_value}'. "
            f"Must be one of: {', '.join(VALID_EVICTION_POLICIES)}"
        )

    def test_invalid_lru_policy_removed(self):
        """Verify the invalid 'lru' policy (bare, without prefix) is no longer present."""
        result = subprocess.run(
            ["grep", "-E", "^maxmemory-policy", REDIS_CONFIG_PATH],
            capture_output=True,
            text=True
        )
        policy_line = result.stdout.strip()
        parts = policy_line.split()

        if len(parts) >= 2:
            policy_value = parts[1]
            # The bare 'lru' is invalid - must have a prefix like allkeys- or volatile-
            assert policy_value != "lru", (
                "The invalid 'maxmemory-policy lru' is still present. "
                "Redis does not accept bare 'lru' as a policy value. "
                "Use 'allkeys-lru' or 'volatile-lru' instead."
            )


class TestRedisServerStarts:
    """Test that Redis server starts successfully with the fixed configuration."""

    def test_redis_server_starts_with_config(self):
        """Verify redis-server can start with the fixed configuration."""
        # First, make sure no Redis is running
        subprocess.run(["pkill", "-9", "redis-server"], capture_output=True)
        time.sleep(0.5)

        # Try to start Redis with the config file
        process = subprocess.Popen(
            ["redis-server", REDIS_CONFIG_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Give Redis time to start
        time.sleep(2)

        # Check if the process is still running (didn't crash immediately)
        poll_result = process.poll()

        if poll_result is not None:
            # Process exited - get the error output
            stdout, stderr = process.communicate()
            pytest.fail(
                f"Redis server failed to start with exit code {poll_result}. "
                f"stdout: {stdout.decode()[:500]}... "
                f"stderr: {stderr.decode()[:500]}..."
            )

        # Process is running, clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    def test_redis_cli_ping_responds(self):
        """Verify redis-cli PING returns PONG after the server starts."""
        # First, make sure no Redis is running
        subprocess.run(["pkill", "-9", "redis-server"], capture_output=True)
        time.sleep(0.5)

        # Start Redis with the config file
        process = subprocess.Popen(
            ["redis-server", REDIS_CONFIG_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            # Give Redis time to start and be ready
            time.sleep(2)

            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                pytest.fail(
                    f"Redis server exited unexpectedly. "
                    f"stderr: {stderr.decode()[:500]}..."
                )

            # Try to ping Redis
            ping_result = subprocess.run(
                ["redis-cli", "PING"],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert ping_result.returncode == 0, (
                f"redis-cli PING failed with exit code {ping_result.returncode}. "
                f"stderr: {ping_result.stderr}"
            )

            assert "PONG" in ping_result.stdout, (
                f"Expected 'PONG' response from redis-cli PING, "
                f"but got: '{ping_result.stdout.strip()}'"
            )

        finally:
            # Clean up - stop the Redis server
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


class TestConfigIntegrity:
    """Test that other configuration lines remain unchanged."""

    def test_config_has_reasonable_content(self):
        """Verify the config file still has reasonable content (not truncated/corrupted)."""
        with open(REDIS_CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        # Should still have approximately the same number of lines
        assert len(lines) >= 10, (
            f"Config file seems truncated. Only {len(lines)} lines found. "
            "Expected approximately 15 lines of configuration."
        )

    def test_fix_is_in_config_file_not_commandline(self):
        """Verify the fix is in redis.conf itself, not bypassed via command-line."""
        # This test ensures the grep of the config file shows a valid policy
        result = subprocess.run(
            ["grep", "-E", "^maxmemory-policy", REDIS_CONFIG_PATH],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            "The maxmemory-policy line must be present in redis.conf. "
            "The fix must be in the config file itself, not via command-line overrides."
        )

        policy_line = result.stdout.strip()
        parts = policy_line.split()
        assert len(parts) >= 2, (
            f"Invalid maxmemory-policy line: '{policy_line}'"
        )

        policy_value = parts[1]
        assert policy_value in VALID_EVICTION_POLICIES, (
            f"The maxmemory-policy in redis.conf must be a valid value. "
            f"Found: '{policy_value}'. "
            f"Valid options: {', '.join(VALID_EVICTION_POLICIES)}"
        )
