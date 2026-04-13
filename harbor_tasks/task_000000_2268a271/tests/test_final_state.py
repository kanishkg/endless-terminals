# test_final_state.py
"""
Tests to validate the final state of the operating system/filesystem
after the student has completed the deployment archive creation task.
"""

import os
import tarfile
import subprocess
import pytest


class TestArchiveFileExists:
    """Test that the archive file was created correctly."""

    def test_archive_file_exists(self):
        """The tar.gz archive must exist at the specified location."""
        archive_path = "/home/user/deployments/app_release_v2.3.1.tar.gz"
        assert os.path.isfile(archive_path), (
            f"Archive file '{archive_path}' does not exist. "
            "You need to create a gzip-compressed tar archive at this location."
        )

    def test_archive_file_is_not_empty(self):
        """The archive file must not be empty."""
        archive_path = "/home/user/deployments/app_release_v2.3.1.tar.gz"
        if os.path.isfile(archive_path):
            assert os.path.getsize(archive_path) > 0, (
                f"Archive file '{archive_path}' exists but is empty. "
                "The archive should contain the application files."
            )


class TestArchiveIsValidGzipTar:
    """Test that the archive is a valid gzip-compressed tar file."""

    def test_archive_is_valid_gzip(self):
        """The archive must be a valid gzip file."""
        archive_path = "/home/user/deployments/app_release_v2.3.1.tar.gz"
        if os.path.isfile(archive_path):
            # Check gzip magic number
            with open(archive_path, 'rb') as f:
                magic = f.read(2)
            assert magic == b'\x1f\x8b', (
                f"File '{archive_path}' is not a valid gzip file. "
                "The archive must be gzip-compressed (use 'tar -czvf' or similar)."
            )

    def test_archive_is_valid_tarfile(self):
        """The archive must be a valid tar file that can be opened."""
        archive_path = "/home/user/deployments/app_release_v2.3.1.tar.gz"
        if os.path.isfile(archive_path):
            try:
                with tarfile.open(archive_path, 'r:gz') as tar:
                    # Just verify we can get the list of members
                    members = tar.getnames()
                    assert len(members) > 0, (
                        f"Archive '{archive_path}' is valid but contains no files."
                    )
            except tarfile.TarError as e:
                pytest.fail(
                    f"Archive '{archive_path}' is not a valid tar.gz file: {e}"
                )


class TestArchiveContents:
    """Test that the archive contains all required files and directories."""

    def get_archive_contents(self):
        """Helper to get the list of paths in the archive."""
        archive_path = "/home/user/deployments/app_release_v2.3.1.tar.gz"
        if os.path.isfile(archive_path):
            try:
                with tarfile.open(archive_path, 'r:gz') as tar:
                    return tar.getnames()
            except tarfile.TarError:
                return []
        return []

    def normalize_path(self, path):
        """Normalize path by removing trailing slashes."""
        return path.rstrip('/')

    def test_archive_contains_root_directory(self):
        """The archive must contain app_release_v2.3.1 as root directory."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]

        # Check if root directory exists (either as explicit entry or as prefix)
        has_root = (
            "app_release_v2.3.1" in normalized or
            any(p.startswith("app_release_v2.3.1/") for p in normalized)
        )
        assert has_root, (
            "Archive does not contain 'app_release_v2.3.1' as the root directory. "
            "The archive must preserve the directory structure with 'app_release_v2.3.1' as root."
        )

    def test_archive_contains_main_py(self):
        """The archive must contain main.py."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]
        assert "app_release_v2.3.1/main.py" in normalized, (
            "Archive does not contain 'app_release_v2.3.1/main.py'. "
            f"Archive contents: {normalized}"
        )

    def test_archive_contains_config_json(self):
        """The archive must contain config.json."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]
        assert "app_release_v2.3.1/config.json" in normalized, (
            "Archive does not contain 'app_release_v2.3.1/config.json'. "
            f"Archive contents: {normalized}"
        )

    def test_archive_contains_requirements_txt(self):
        """The archive must contain requirements.txt."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]
        assert "app_release_v2.3.1/requirements.txt" in normalized, (
            "Archive does not contain 'app_release_v2.3.1/requirements.txt'. "
            f"Archive contents: {normalized}"
        )

    def test_archive_contains_readme_md(self):
        """The archive must contain README.md."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]
        assert "app_release_v2.3.1/README.md" in normalized, (
            "Archive does not contain 'app_release_v2.3.1/README.md'. "
            f"Archive contents: {normalized}"
        )

    def test_archive_contains_lib_directory(self):
        """The archive must contain the lib subdirectory."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]

        # Check if lib directory exists (either as explicit entry or implied by files)
        has_lib = (
            "app_release_v2.3.1/lib" in normalized or
            any(p.startswith("app_release_v2.3.1/lib/") for p in normalized)
        )
        assert has_lib, (
            "Archive does not contain 'app_release_v2.3.1/lib/' subdirectory. "
            f"Archive contents: {normalized}"
        )

    def test_archive_contains_utils_py(self):
        """The archive must contain lib/utils.py."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]
        assert "app_release_v2.3.1/lib/utils.py" in normalized, (
            "Archive does not contain 'app_release_v2.3.1/lib/utils.py'. "
            f"Archive contents: {normalized}"
        )

    def test_archive_contains_database_py(self):
        """The archive must contain lib/database.py."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]
        assert "app_release_v2.3.1/lib/database.py" in normalized, (
            "Archive does not contain 'app_release_v2.3.1/lib/database.py'. "
            f"Archive contents: {normalized}"
        )

    def test_archive_contains_all_required_items(self):
        """The archive must contain all 8 required items (2 dirs + 6 files)."""
        contents = self.get_archive_contents()
        normalized = [self.normalize_path(p) for p in contents]

        required_files = [
            "app_release_v2.3.1/main.py",
            "app_release_v2.3.1/config.json",
            "app_release_v2.3.1/requirements.txt",
            "app_release_v2.3.1/README.md",
            "app_release_v2.3.1/lib/utils.py",
            "app_release_v2.3.1/lib/database.py",
        ]

        missing = [f for f in required_files if f not in normalized]
        assert len(missing) == 0, (
            f"Archive is missing the following required files: {missing}. "
            f"Archive contents: {normalized}"
        )


class TestLogFileExists:
    """Test that the verification log file was created correctly."""

    def test_log_file_exists(self):
        """The archive_contents.log file must exist."""
        log_path = "/home/user/deployments/archive_contents.log"
        assert os.path.isfile(log_path), (
            f"Log file '{log_path}' does not exist. "
            "You need to create a log file containing the verbose listing of archive contents."
        )

    def test_log_file_is_not_empty(self):
        """The log file must not be empty."""
        log_path = "/home/user/deployments/archive_contents.log"
        if os.path.isfile(log_path):
            assert os.path.getsize(log_path) > 0, (
                f"Log file '{log_path}' exists but is empty. "
                "It should contain the verbose listing of the archive contents."
            )


class TestLogFileContents:
    """Test that the log file contains the required information."""

    def get_log_contents(self):
        """Helper to read the log file contents."""
        log_path = "/home/user/deployments/archive_contents.log"
        if os.path.isfile(log_path):
            with open(log_path, 'r') as f:
                return f.read()
        return ""

    def test_log_contains_main_py(self):
        """Log file must reference main.py."""
        contents = self.get_log_contents()
        assert "main.py" in contents, (
            "Log file does not contain reference to 'main.py'. "
            "The log should list all files in the archive."
        )

    def test_log_contains_config_json(self):
        """Log file must reference config.json."""
        contents = self.get_log_contents()
        assert "config.json" in contents, (
            "Log file does not contain reference to 'config.json'. "
            "The log should list all files in the archive."
        )

    def test_log_contains_requirements_txt(self):
        """Log file must reference requirements.txt."""
        contents = self.get_log_contents()
        assert "requirements.txt" in contents, (
            "Log file does not contain reference to 'requirements.txt'. "
            "The log should list all files in the archive."
        )

    def test_log_contains_readme_md(self):
        """Log file must reference README.md."""
        contents = self.get_log_contents()
        assert "README.md" in contents, (
            "Log file does not contain reference to 'README.md'. "
            "The log should list all files in the archive."
        )

    def test_log_contains_utils_py(self):
        """Log file must reference utils.py."""
        contents = self.get_log_contents()
        assert "utils.py" in contents, (
            "Log file does not contain reference to 'utils.py'. "
            "The log should list all files in the archive."
        )

    def test_log_contains_database_py(self):
        """Log file must reference database.py."""
        contents = self.get_log_contents()
        assert "database.py" in contents, (
            "Log file does not contain reference to 'database.py'. "
            "The log should list all files in the archive."
        )

    def test_log_contains_lib_directory(self):
        """Log file must reference the lib directory."""
        contents = self.get_log_contents()
        assert "lib" in contents, (
            "Log file does not contain reference to 'lib' directory. "
            "The log should list all directories in the archive."
        )

    def test_log_contains_app_release_directory(self):
        """Log file must reference the app_release_v2.3.1 directory."""
        contents = self.get_log_contents()
        assert "app_release_v2.3.1" in contents, (
            "Log file does not contain reference to 'app_release_v2.3.1' directory. "
            "The log should show the root directory of the archive."
        )

    def test_log_appears_to_be_verbose_listing(self):
        """Log file should appear to be a verbose tar listing (contains typical elements)."""
        contents = self.get_log_contents()
        # Verbose tar listings typically contain permission strings like 'rwx' or '-'
        # and date/time information
        has_permissions = ('rwx' in contents or 'r--' in contents or 
                          'rw-' in contents or '-rw' in contents or
                          'drwx' in contents)
        has_paths = 'app_release_v2.3.1' in contents

        assert has_paths, (
            "Log file does not appear to contain proper archive listing. "
            "Use 'tar -tzvf' or similar to generate a verbose listing."
        )


class TestArchiveExtraction:
    """Test that the archive can be properly extracted with correct contents."""

    def test_archive_files_have_content(self):
        """Files in the archive should have content (not be empty)."""
        archive_path = "/home/user/deployments/app_release_v2.3.1.tar.gz"
        if os.path.isfile(archive_path):
            try:
                with tarfile.open(archive_path, 'r:gz') as tar:
                    for member in tar.getmembers():
                        if member.isfile():
                            assert member.size > 0, (
                                f"File '{member.name}' in archive is empty. "
                                "All application files should have content."
                            )
            except tarfile.TarError as e:
                pytest.fail(f"Could not read archive: {e}")
