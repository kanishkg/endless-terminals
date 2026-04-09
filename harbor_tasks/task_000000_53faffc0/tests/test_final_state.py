# test_final_state.py
"""
Tests to validate the final state of the operating system after the student
has completed the API integration and data pipeline task.
"""

import os
import pytest
import subprocess
import stat
import time


class TestFinalState:
    """Test the final state after completing the API integration task."""

    def test_data_pipeline_script_exists(self):
        """Verify the data pipeline script exists at /home/user/data_pipeline.sh."""
        script_path = "/home/user/data_pipeline.sh"
        assert os.path.isfile(script_path), (
            f"Data pipeline script not found at {script_path}. "
            "The task requires creating this shell script."
        )

    def test_data_pipeline_script_is_executable(self):
        """Verify the data pipeline script is executable."""
        script_path = "/home/user/data_pipeline.sh"
        assert os.path.isfile(script_path), (
            f"Cannot check executable status: {script_path} does not exist"
        )

        file_stat = os.stat(script_path)
        is_executable = file_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        assert is_executable, (
            f"Data pipeline script at {script_path} is not executable. "
            "The script should have execute permissions (chmod +x)."
        )

    def test_pipeline_results_file_exists(self):
        """Verify the pipeline results file exists at /home/user/pipeline_results.log."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Pipeline results file not found at {results_path}. "
            "The task requires running the pipeline and generating this output file."
        )

    def test_pipeline_results_has_users_endpoint(self):
        """Verify the results file contains the /api/users endpoint section."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        assert "ENDPOINT: /api/users" in content, (
            "Results file is missing 'ENDPOINT: /api/users' entry. "
            "The pipeline should log results for the /api/users endpoint."
        )

    def test_pipeline_results_has_products_endpoint(self):
        """Verify the results file contains the /api/products endpoint section."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        assert "ENDPOINT: /api/products" in content, (
            "Results file is missing 'ENDPOINT: /api/products' entry. "
            "The pipeline should log results for the /api/products endpoint."
        )

    def test_pipeline_results_has_orders_endpoint(self):
        """Verify the results file contains the /api/orders endpoint section."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        assert "ENDPOINT: /api/orders" in content, (
            "Results file is missing 'ENDPOINT: /api/orders' entry. "
            "The pipeline should log results for the /api/orders endpoint."
        )

    def test_pipeline_results_users_success(self):
        """Verify the /api/users endpoint shows SUCCESS status."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        # Find the users section and check for SUCCESS
        lines = content.split('\n')
        found_users = False
        found_success = False
        for i, line in enumerate(lines):
            if "ENDPOINT: /api/users" in line:
                found_users = True
                # Check the next few lines for STATUS: SUCCESS
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "STATUS: SUCCESS" in lines[j]:
                        found_success = True
                        break
                    if "ENDPOINT:" in lines[j]:
                        break
                break

        assert found_users and found_success, (
            "The /api/users endpoint should have 'STATUS: SUCCESS'. "
            "This endpoint returns valid data and should be successful."
        )

    def test_pipeline_results_users_count(self):
        """Verify the /api/users endpoint shows COUNT: 3."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        # Find the users section and check for COUNT: 3
        lines = content.split('\n')
        found_users = False
        found_count = False
        for i, line in enumerate(lines):
            if "ENDPOINT: /api/users" in line:
                found_users = True
                # Check the next few lines for COUNT: 3
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "COUNT: 3" in lines[j]:
                        found_count = True
                        break
                    if "ENDPOINT:" in lines[j]:
                        break
                break

        assert found_users and found_count, (
            "The /api/users endpoint should have 'COUNT: 3'. "
            "The mock API returns 3 users (Alice, Bob, Charlie)."
        )

    def test_pipeline_results_products_success(self):
        """Verify the /api/products endpoint shows SUCCESS status."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        # Find the products section and check for SUCCESS
        lines = content.split('\n')
        found_products = False
        found_success = False
        for i, line in enumerate(lines):
            if "ENDPOINT: /api/products" in line:
                found_products = True
                # Check the next few lines for STATUS: SUCCESS
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "STATUS: SUCCESS" in lines[j]:
                        found_success = True
                        break
                    if "ENDPOINT:" in lines[j]:
                        break
                break

        assert found_products and found_success, (
            "The /api/products endpoint should have 'STATUS: SUCCESS'. "
            "This endpoint returns valid data and should be successful."
        )

    def test_pipeline_results_products_count(self):
        """Verify the /api/products endpoint shows COUNT: 2."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        # Find the products section and check for COUNT: 2
        lines = content.split('\n')
        found_products = False
        found_count = False
        for i, line in enumerate(lines):
            if "ENDPOINT: /api/products" in line:
                found_products = True
                # Check the next few lines for COUNT: 2
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "COUNT: 2" in lines[j]:
                        found_count = True
                        break
                    if "ENDPOINT:" in lines[j]:
                        break
                break

        assert found_products and found_count, (
            "The /api/products endpoint should have 'COUNT: 2'. "
            "The mock API returns 2 products (Widget, Gadget)."
        )

    def test_pipeline_results_orders_error(self):
        """Verify the /api/orders endpoint shows ERROR status."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        # Find the orders section and check for ERROR
        lines = content.split('\n')
        found_orders = False
        found_error = False
        for i, line in enumerate(lines):
            if "ENDPOINT: /api/orders" in line:
                found_orders = True
                # Check the next few lines for STATUS: ERROR
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "STATUS: ERROR" in lines[j]:
                        found_error = True
                        break
                    if "ENDPOINT:" in lines[j]:
                        break
                break

        assert found_orders and found_error, (
            "The /api/orders endpoint should have 'STATUS: ERROR'. "
            "This endpoint returns a 500 error and should be logged as an error."
        )

    def test_pipeline_results_orders_error_code(self):
        """Verify the /api/orders endpoint shows ERROR_CODE: 500."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        # Find the orders section and check for ERROR_CODE: 500
        lines = content.split('\n')
        found_orders = False
        found_error_code = False
        for i, line in enumerate(lines):
            if "ENDPOINT: /api/orders" in line:
                found_orders = True
                # Check the next few lines for ERROR_CODE: 500
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "ERROR_CODE: 500" in lines[j]:
                        found_error_code = True
                        break
                    if "ENDPOINT:" in lines[j]:
                        break
                break

        assert found_orders and found_error_code, (
            "The /api/orders endpoint should have 'ERROR_CODE: 500'. "
            "The mock API returns HTTP 500 for this endpoint."
        )

    def test_pipeline_results_exact_format(self):
        """Verify the pipeline results file has the exact expected format."""
        results_path = "/home/user/pipeline_results.log"
        assert os.path.isfile(results_path), (
            f"Cannot check content: {results_path} does not exist"
        )

        with open(results_path, 'r') as f:
            content = f.read()

        expected_content = """ENDPOINT: /api/users
STATUS: SUCCESS
COUNT: 3

ENDPOINT: /api/products
STATUS: SUCCESS
COUNT: 2

ENDPOINT: /api/orders
STATUS: ERROR
ERROR_CODE: 500
"""

        # Normalize line endings and trailing whitespace
        content_normalized = '\n'.join(line.rstrip() for line in content.strip().split('\n'))
        expected_normalized = '\n'.join(line.rstrip() for line in expected_content.strip().split('\n'))

        assert content_normalized == expected_normalized, (
            f"Pipeline results file does not match expected format.\n"
            f"Expected:\n{expected_content}\n"
            f"Got:\n{content}"
        )

    def test_api_server_not_running(self):
        """Verify the API server process is not running after task completion."""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'api_server.py'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # pgrep returns 0 if process found, 1 if not found
            assert result.returncode != 0 or result.stdout.strip() == '', (
                f"API server process is still running (PIDs: {result.stdout.strip()}). "
                "The task requires stopping the API server after running the pipeline."
            )
        except FileNotFoundError:
            # Try alternative method using ps
            try:
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                assert 'api_server.py' not in result.stdout, (
                    "API server process is still running. "
                    "The task requires stopping the API server after running the pipeline."
                )
            except FileNotFoundError:
                pytest.skip("Cannot verify process status: pgrep and ps not available")

    def test_port_8765_is_free(self):
        """Verify port 8765 is not in use after task completion."""
        # Try using lsof to check if port is in use
        try:
            result = subprocess.run(
                ['lsof', '-i', ':8765'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # lsof returns 0 if it finds something, 1 if nothing found
            assert result.returncode != 0 or result.stdout.strip() == '', (
                f"Port 8765 is still in use after task completion. Output: {result.stdout}. "
                "The task requires stopping the API server, which should free this port."
            )
        except FileNotFoundError:
            # lsof not available, try ss
            try:
                result = subprocess.run(
                    ['ss', '-tuln'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                assert ':8765' not in result.stdout, (
                    "Port 8765 is still in use after task completion. "
                    "The task requires stopping the API server, which should free this port."
                )
            except FileNotFoundError:
                # Neither lsof nor ss available, try netstat
                try:
                    result = subprocess.run(
                        ['netstat', '-tuln'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    assert ':8765' not in result.stdout, (
                        "Port 8765 is still in use after task completion. "
                        "The task requires stopping the API server, which should free this port."
                    )
                except FileNotFoundError:
                    pytest.skip("Cannot verify port status: lsof, ss, and netstat not available")

    def test_api_server_script_still_exists(self):
        """Verify the original API server script still exists (wasn't deleted)."""
        api_server_path = "/home/user/api_server.py"
        assert os.path.isfile(api_server_path), (
            f"API server script at {api_server_path} was deleted. "
            "The task only requires stopping the server, not removing the script."
        )
