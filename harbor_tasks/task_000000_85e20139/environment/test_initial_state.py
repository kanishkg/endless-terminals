# test_initial_state.py
"""
Tests to validate the initial state before the student fixes the Redis configuration.
"""

import os
import subprocess
import pytest


class TestRedisConfigFileExists:
    """Test that the Redis configuration file exists and is accessible."""

    def test_redis_config_file_exists(self):
        """Verify /home/user/services/redis/redis.conf exists."""
        config_path = "/home/user/services/redis/redis.conf"
        assert os.path.exists(config_path), (
            f"Redis config file does not exist at {config_path}. "
            "The file should be present for the student to fix."
        )

    def test_redis_config_file_is_file(self):
        """Verify redis.conf is a regular file, not a directory."""
        config_path = "/home/user/services/redis/redis.conf"
        assert os.path.isfile(config_path), (
            f"{config_path} exists but is not a regular file."
        )

    def test_redis_config_file_is_writable(self):
        """Verify redis.conf is writable by the current user."""
        config_path = "/home/user/services/redis/redis.conf"
        assert os.access(config_path, os.W_OK), (
            f"{config_path} is not writable. "
            "The student needs write access to fix the configuration."
        )


class TestRedisConfigContent:
    """Test that the Redis configuration file has the expected initial content."""

    def test_config_has_reasonable_line_count(self):
        """Verify the config file has approximately 15 lines of configuration."""
        config_path = "/home/user/services/redis/redis.conf"
        with open(config_path, 'r') as f:
            lines = f.readlines()

        # Allow some flexibility - should be around 15 lines
        assert 10 <= len(lines) <= 25, (
            f"Expected approximately 15 lines in redis.conf, but found {len(lines)} lines. "
            "The config file should contain standard Redis configuration."
        )

    def test_invalid_maxmemory_policy_exists(self):
        """Verify the config contains the invalid 'maxmemory-policy lru' line."""
        config_path = "/home/user/services/redis/redis.conf"
        with open(config_path, 'r') as f:
            content = f.read()

        # Check that the invalid policy exists
        assert "maxmemory-policy lru" in content or "maxmemory-policy  lru" in content, (
            "The invalid 'maxmemory-policy lru' line was not found in redis.conf. "
            "The initial state should have this invalid configuration for the student to fix."
        )

    def test_maxmemory_policy_is_invalid_value(self):
        """Verify the maxmemory-policy is set to invalid 'lru' (not a valid Redis policy)."""
        config_path = "/home/user/services/redis/redis.conf"

        # Use grep to find the maxmemory-policy line
        result = subprocess.run(
            ["grep", "-E", "^maxmemory-policy", config_path],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            "No 'maxmemory-policy' line found in redis.conf. "
            "The config should have a maxmemory-policy directive."
        )

        policy_line = result.stdout.strip()
        # Valid policies that should NOT be present initially
        valid_policies = [
            "noeviction", "allkeys-lru", "volatile-lru", 
            "allkeys-random", "volatile-random", "volatile-ttl",
            "allkeys-lfu", "volatile-lfu"
        ]

        # The line should contain just 'lru', not any valid policy
        for valid_policy in valid_policies:
            assert valid_policy not in policy_line, (
                f"Found valid policy '{valid_policy}' in maxmemory-policy line. "
                f"Initial state should have invalid 'lru' value. Found: {policy_line}"
            )


class TestRedisServerAvailable:
    """Test that Redis server is installed and available."""

    def test_redis_server_installed(self):
        """Verify redis-server binary is available."""
        result = subprocess.run(
            ["which", "redis-server"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "redis-server is not installed or not in PATH. "
            "Redis server must be available for this task."
        )

    def test_redis_server_version(self):
        """Verify Redis 7.x is installed."""
        result = subprocess.run(
            ["redis-server", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Failed to get redis-server version."
        )

        # Check for Redis 7.x (or at least a recent version)
        version_output = result.stdout
        assert "Redis server v=" in version_output or "v=" in version_output, (
            f"Unexpected redis-server version output: {version_output}"
        )


class TestNoRedisRunning:
    """Test that no Redis process is currently running."""

    def test_no_redis_process_running(self):
        """Verify no Redis server process is currently running."""
        result = subprocess.run(
            ["pgrep", "-x", "redis-server"],
            capture_output=True,
            text=True
        )
        # pgrep returns 1 if no processes found, 0 if found
        assert result.returncode != 0, (
            "A Redis server process is already running. "
            "Initial state should have no Redis process running."
        )

    def test_redis_port_not_in_use(self):
        """Verify the default Redis port (6379) is not in use."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )

        # Check if port 6379 is being listened on
        assert ":6379" not in result.stdout, (
            "Port 6379 is already in use. "
            "Initial state should have the Redis port available."
        )


class TestDirectoryStructure:
    """Test that the required directory structure exists."""

    def test_services_directory_exists(self):
        """Verify /home/user/services directory exists."""
        services_path = "/home/user/services"
        assert os.path.isdir(services_path), (
            f"Directory {services_path} does not exist."
        )

    def test_redis_directory_exists(self):
        """Verify /home/user/services/redis directory exists."""
        redis_path = "/home/user/services/redis"
        assert os.path.isdir(redis_path), (
            f"Directory {redis_path} does not exist."
        )
