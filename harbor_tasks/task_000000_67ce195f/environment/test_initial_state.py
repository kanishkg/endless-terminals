# test_initial_state.py
"""
Tests to validate the initial state of the operating system before the student
performs the PostgreSQL backup task.
"""

import os
import pytest


class TestSourceDirectoryExists:
    """Tests for the source postgres_config directory."""

    def test_postgres_config_directory_exists(self):
        """The source directory /home/user/postgres_config must exist."""
        path = "/home/user/postgres_config"
        assert os.path.exists(path), (
            f"Source directory '{path}' does not exist. "
            "This directory should contain the PostgreSQL configuration files to backup."
        )

    def test_postgres_config_is_directory(self):
        """The postgres_config path must be a directory, not a file."""
        path = "/home/user/postgres_config"
        assert os.path.isdir(path), (
            f"'{path}' exists but is not a directory. "
            "It should be a directory containing PostgreSQL configuration files."
        )


class TestConfigurationFilesExist:
    """Tests for the required PostgreSQL configuration files."""

    def test_postgresql_conf_exists(self):
        """The postgresql.conf file must exist in the source directory."""
        path = "/home/user/postgres_config/postgresql.conf"
        assert os.path.exists(path), (
            f"Configuration file '{path}' does not exist. "
            "This is a required PostgreSQL configuration file for the backup."
        )

    def test_postgresql_conf_is_file(self):
        """The postgresql.conf must be a regular file."""
        path = "/home/user/postgres_config/postgresql.conf"
        assert os.path.isfile(path), (
            f"'{path}' exists but is not a regular file. "
            "It should be a PostgreSQL configuration file."
        )

    def test_pg_hba_conf_exists(self):
        """The pg_hba.conf file must exist in the source directory."""
        path = "/home/user/postgres_config/pg_hba.conf"
        assert os.path.exists(path), (
            f"Configuration file '{path}' does not exist. "
            "This is a required PostgreSQL host-based authentication configuration file."
        )

    def test_pg_hba_conf_is_file(self):
        """The pg_hba.conf must be a regular file."""
        path = "/home/user/postgres_config/pg_hba.conf"
        assert os.path.isfile(path), (
            f"'{path}' exists but is not a regular file. "
            "It should be a PostgreSQL configuration file."
        )

    def test_recovery_conf_exists(self):
        """The recovery.conf file must exist in the source directory."""
        path = "/home/user/postgres_config/recovery.conf"
        assert os.path.exists(path), (
            f"Configuration file '{path}' does not exist. "
            "This is a required PostgreSQL recovery configuration file."
        )

    def test_recovery_conf_is_file(self):
        """The recovery.conf must be a regular file."""
        path = "/home/user/postgres_config/recovery.conf"
        assert os.path.isfile(path), (
            f"'{path}' exists but is not a regular file. "
            "It should be a PostgreSQL configuration file."
        )


class TestConfigurationFileContents:
    """Tests to verify the configuration files have expected content."""

    def test_postgresql_conf_has_content(self):
        """The postgresql.conf file should not be empty."""
        path = "/home/user/postgres_config/postgresql.conf"
        if os.path.exists(path):
            size = os.path.getsize(path)
            assert size > 0, (
                f"Configuration file '{path}' is empty. "
                "It should contain PostgreSQL configuration settings."
            )

    def test_pg_hba_conf_has_content(self):
        """The pg_hba.conf file should not be empty."""
        path = "/home/user/postgres_config/pg_hba.conf"
        if os.path.exists(path):
            size = os.path.getsize(path)
            assert size > 0, (
                f"Configuration file '{path}' is empty. "
                "It should contain host-based authentication rules."
            )

    def test_recovery_conf_has_content(self):
        """The recovery.conf file should not be empty."""
        path = "/home/user/postgres_config/recovery.conf"
        if os.path.exists(path):
            size = os.path.getsize(path)
            assert size > 0, (
                f"Configuration file '{path}' is empty. "
                "It should contain recovery configuration settings."
            )


class TestBackupsDirectoryPreCondition:
    """Tests for the backups directory initial state."""

    def test_backups_directory_exists(self):
        """The /home/user/backups directory must exist for storing the backup."""
        path = "/home/user/backups"
        assert os.path.exists(path), (
            f"Backups directory '{path}' does not exist. "
            "This directory is needed to store the backup archive and verification log."
        )

    def test_backups_is_directory(self):
        """The backups path must be a directory."""
        path = "/home/user/backups"
        assert os.path.isdir(path), (
            f"'{path}' exists but is not a directory. "
            "It should be a directory for storing backup files."
        )


class TestHomeDirectoryExists:
    """Tests for the home directory structure."""

    def test_home_user_directory_exists(self):
        """The /home/user directory must exist."""
        path = "/home/user"
        assert os.path.exists(path), (
            f"Home directory '{path}' does not exist. "
            "This is the base directory for the task."
        )

    def test_home_user_is_directory(self):
        """The /home/user path must be a directory."""
        path = "/home/user"
        assert os.path.isdir(path), (
            f"'{path}' exists but is not a directory. "
            "It should be the user's home directory."
        )
