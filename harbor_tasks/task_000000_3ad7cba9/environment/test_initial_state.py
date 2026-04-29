# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the certificate expiry extraction task.
"""

import os
import subprocess
import pytest


class TestInitialState:
    """Test suite to validate initial state before task execution."""

    def test_certs_directory_exists(self):
        """Verify that /home/user/certs/ directory exists."""
        certs_dir = "/home/user/certs"
        assert os.path.isdir(certs_dir), (
            f"Directory {certs_dir} does not exist. "
            "The certs directory must exist before the task can be performed."
        )

    def test_webapp_pem_exists(self):
        """Verify that /home/user/certs/webapp.pem file exists."""
        cert_path = "/home/user/certs/webapp.pem"
        assert os.path.isfile(cert_path), (
            f"Certificate file {cert_path} does not exist. "
            "The webapp.pem certificate must be present."
        )

    def test_webapp_pem_is_readable(self):
        """Verify that /home/user/certs/webapp.pem is readable."""
        cert_path = "/home/user/certs/webapp.pem"
        assert os.access(cert_path, os.R_OK), (
            f"Certificate file {cert_path} is not readable. "
            "The certificate must be readable to extract expiry information."
        )

    def test_webapp_pem_is_valid_certificate(self):
        """Verify that /home/user/certs/webapp.pem is a valid PEM-encoded X.509 certificate."""
        cert_path = "/home/user/certs/webapp.pem"
        result = subprocess.run(
            ["openssl", "x509", "-in", cert_path, "-noout", "-text"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Certificate file {cert_path} is not a valid PEM-encoded X.509 certificate. "
            f"OpenSSL error: {result.stderr}"
        )

    def test_webapp_pem_has_correct_expiry_date(self):
        """Verify that the certificate's notAfter field is 'Mar 15 09:30:45 2025 GMT'."""
        cert_path = "/home/user/certs/webapp.pem"
        result = subprocess.run(
            ["openssl", "x509", "-enddate", "-noout", "-in", cert_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to read expiry date from {cert_path}. "
            f"OpenSSL error: {result.stderr}"
        )

        # Output format is: notAfter=Mar 15 09:30:45 2025 GMT
        expected_date = "Mar 15 09:30:45 2025 GMT"
        output = result.stdout.strip()
        assert expected_date in output, (
            f"Certificate expiry date does not match expected value. "
            f"Expected notAfter to contain '{expected_date}', but got: '{output}'"
        )

    def test_report_directory_exists(self):
        """Verify that /home/user/report/ directory exists."""
        report_dir = "/home/user/report"
        assert os.path.isdir(report_dir), (
            f"Directory {report_dir} does not exist. "
            "The report directory must exist before the task can be performed."
        )

    def test_report_directory_is_writable(self):
        """Verify that /home/user/report/ directory is writable."""
        report_dir = "/home/user/report"
        assert os.access(report_dir, os.W_OK), (
            f"Directory {report_dir} is not writable. "
            "The report directory must be writable to create the output file."
        )

    def test_cert_expiry_txt_does_not_exist(self):
        """Verify that /home/user/report/cert_expiry.txt does not exist yet."""
        output_file = "/home/user/report/cert_expiry.txt"
        assert not os.path.exists(output_file), (
            f"Output file {output_file} already exists. "
            "The output file should not exist before the task is performed."
        )

    def test_openssl_is_installed(self):
        """Verify that openssl is installed and available."""
        result = subprocess.run(
            ["which", "openssl"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "OpenSSL is not installed or not in PATH. "
            "OpenSSL must be available to extract certificate information."
        )

    def test_openssl_is_functional(self):
        """Verify that openssl can be executed."""
        result = subprocess.run(
            ["openssl", "version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "OpenSSL is not functional. "
            f"Error: {result.stderr}"
        )
