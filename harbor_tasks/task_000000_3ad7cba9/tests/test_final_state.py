# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the certificate expiry extraction task.
"""

import os
import subprocess
import pytest


class TestFinalState:
    """Test suite to validate final state after task execution."""

    def test_cert_expiry_txt_exists(self):
        """Verify that /home/user/report/cert_expiry.txt exists."""
        output_file = "/home/user/report/cert_expiry.txt"
        assert os.path.isfile(output_file), (
            f"Output file {output_file} does not exist. "
            "The task requires creating this file with the certificate expiry date."
        )

    def test_cert_expiry_txt_is_readable(self):
        """Verify that /home/user/report/cert_expiry.txt is readable."""
        output_file = "/home/user/report/cert_expiry.txt"
        assert os.access(output_file, os.R_OK), (
            f"Output file {output_file} is not readable."
        )

    def test_cert_expiry_txt_contains_correct_format(self):
        """Verify that cert_expiry.txt contains the date in 'YYYY-MM-DD HH:MM:SS UTC' format."""
        output_file = "/home/user/report/cert_expiry.txt"

        with open(output_file, 'r') as f:
            content = f.read()

        # Expected exact content
        expected_content = "2025-03-15 09:30:45 UTC\n"

        assert content == expected_content, (
            f"Content of {output_file} does not match expected format. "
            f"Expected exactly: '2025-03-15 09:30:45 UTC' followed by a newline. "
            f"Got: {repr(content)}"
        )

    def test_cert_expiry_txt_has_exactly_one_line(self):
        """Verify that cert_expiry.txt contains exactly one line."""
        output_file = "/home/user/report/cert_expiry.txt"

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # Should have exactly one line (possibly with trailing newline)
        non_empty_lines = [line for line in lines if line.strip()]

        assert len(non_empty_lines) == 1, (
            f"File {output_file} should contain exactly one line of content. "
            f"Found {len(non_empty_lines)} non-empty lines."
        )

    def test_cert_expiry_txt_no_extra_text(self):
        """Verify that cert_expiry.txt contains no headers, labels, or extra text."""
        output_file = "/home/user/report/cert_expiry.txt"

        with open(output_file, 'r') as f:
            content = f.read().strip()

        # Should not contain common header/label patterns
        forbidden_patterns = ['notAfter', 'expiry', 'date', 'certificate', '=', ':']

        for pattern in forbidden_patterns:
            assert pattern.lower() not in content.lower(), (
                f"File {output_file} contains extra text or labels. "
                f"Found '{pattern}' in content. "
                "The file should contain only the date in 'YYYY-MM-DD HH:MM:SS UTC' format."
            )

    def test_expiry_matches_certificate(self):
        """Verify that the expiry date in cert_expiry.txt matches the actual certificate."""
        cert_path = "/home/user/certs/webapp.pem"
        output_file = "/home/user/report/cert_expiry.txt"

        # Get the actual expiry from the certificate
        result = subprocess.run(
            ["openssl", "x509", "-enddate", "-noout", "-in", cert_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to read expiry date from certificate {cert_path}. "
            f"OpenSSL error: {result.stderr}"
        )

        # Parse the openssl output (format: notAfter=Mar 15 09:30:45 2025 GMT)
        openssl_output = result.stdout.strip()
        assert "Mar 15 09:30:45 2025 GMT" in openssl_output, (
            f"Certificate expiry date has changed unexpectedly. "
            f"OpenSSL output: {openssl_output}"
        )

        # Read the output file
        with open(output_file, 'r') as f:
            file_content = f.read().strip()

        # The expected conversion: Mar 15 09:30:45 2025 GMT -> 2025-03-15 09:30:45 UTC
        expected_date = "2025-03-15 09:30:45 UTC"

        assert file_content == expected_date, (
            f"The expiry date in {output_file} does not correctly represent "
            f"the certificate's expiry date. "
            f"Certificate shows: 'Mar 15 09:30:45 2025 GMT'. "
            f"Expected in file: '{expected_date}'. "
            f"Found in file: '{file_content}'"
        )

    def test_webapp_pem_unchanged(self):
        """Verify that /home/user/certs/webapp.pem is unchanged (still valid with same expiry)."""
        cert_path = "/home/user/certs/webapp.pem"

        # Check certificate is still valid
        result = subprocess.run(
            ["openssl", "x509", "-in", cert_path, "-noout", "-text"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Certificate file {cert_path} is no longer a valid certificate. "
            "The original certificate should not be modified."
        )

        # Check expiry date is still the same
        result = subprocess.run(
            ["openssl", "x509", "-enddate", "-noout", "-in", cert_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to read expiry date from {cert_path}."
        )

        expected_date = "Mar 15 09:30:45 2025 GMT"
        assert expected_date in result.stdout, (
            f"Certificate {cert_path} has been modified. "
            f"Expected expiry date '{expected_date}' not found in certificate."
        )
