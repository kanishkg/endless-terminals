# test_final_state.py
"""
Tests to validate the final state after the student has fixed the JSON validator
performance issue. The benchmark must achieve >= 400 docs/sec throughput.
"""

import os
import subprocess
import sys
import re
import pytest


# Base paths
VALIDATOR_DIR = "/home/user/validator"
SCHEMAS_DIR = os.path.join(VALIDATOR_DIR, "schemas")
TESTDATA_DIR = os.path.join(VALIDATOR_DIR, "testdata")
CACHE_DIR = os.path.join(VALIDATOR_DIR, "cache")
VALIDATE_PY = os.path.join(VALIDATOR_DIR, "validate.py")


class TestDirectoryStructurePreserved:
    """Test that the required directory structure is still intact."""

    def test_validator_directory_exists(self):
        """The /home/user/validator directory must still exist."""
        assert os.path.isdir(VALIDATOR_DIR), (
            f"Directory {VALIDATOR_DIR} does not exist."
        )

    def test_schemas_directory_exists(self):
        """The schemas/ subdirectory must still exist."""
        assert os.path.isdir(SCHEMAS_DIR), (
            f"Directory {SCHEMAS_DIR} does not exist."
        )

    def test_testdata_directory_exists(self):
        """The testdata/ subdirectory must still exist."""
        assert os.path.isdir(TESTDATA_DIR), (
            f"Directory {TESTDATA_DIR} does not exist."
        )

    def test_validate_py_exists(self):
        """The validate.py script must still exist."""
        assert os.path.isfile(VALIDATE_PY), (
            f"File {VALIDATE_PY} does not exist."
        )


class TestFilesPreserved:
    """Test that schema and testdata files are preserved."""

    def test_schemas_directory_has_50_files(self):
        """The schemas/ directory must still contain at least 50 JSON schema files."""
        schema_files = [f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.json')]
        assert len(schema_files) >= 50, (
            f"Expected at least 50 JSON schema files in {SCHEMAS_DIR}, "
            f"found {len(schema_files)}. Schema files must not be deleted."
        )

    def test_testdata_directory_has_200_files(self):
        """The testdata/ directory must still contain at least 200 JSON documents."""
        json_files = [f for f in os.listdir(TESTDATA_DIR) if f.endswith('.json')]
        assert len(json_files) >= 200, (
            f"Expected at least 200 JSON documents in {TESTDATA_DIR}, "
            f"found {len(json_files)}. Test data files must not be deleted."
        )


class TestValidateScriptRequirements:
    """Test that validate.py still meets the required constraints."""

    def test_validate_py_uses_draft7validator(self):
        """validate.py must still use Draft7Validator from jsonschema."""
        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        # Count occurrences of Draft7Validator
        count = content.count('Draft7Validator')
        assert count >= 1, (
            f"validate.py must still use Draft7Validator (found {count} occurrences). "
            "Cannot replace jsonschema with a stub."
        )

    def test_validate_py_uses_jsonschema_import(self):
        """validate.py must still import jsonschema."""
        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        assert 'jsonschema' in content, (
            "validate.py must still use the jsonschema library."
        )

    def test_validate_py_has_benchmark_flag(self):
        """validate.py must still support --benchmark flag."""
        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        assert 'benchmark' in content.lower(), (
            "validate.py must still support the --benchmark flag."
        )

    def test_validate_py_syntax_valid(self):
        """validate.py must have valid Python syntax."""
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', VALIDATE_PY],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"validate.py has syntax errors: {result.stderr}"
        )


class TestJqPreprocessingPreserved:
    """Test that jq preprocessing is still being used."""

    def test_validate_py_calls_jq(self):
        """validate.py must still call jq for preprocessing."""
        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        # Check for jq invocation - could be via subprocess, os.system, etc.
        jq_patterns = ['jq', 'subprocess', 'Popen', 'run(']
        has_jq_reference = 'jq' in content

        assert has_jq_reference, (
            "validate.py must still use jq for preprocessing schemas. "
            "The jq preprocessing step expands $shortref keys and cannot be removed."
        )


class TestBenchmarkPerformance:
    """Test that the benchmark achieves the required performance."""

    def test_benchmark_runs_successfully(self):
        """The benchmark must run without errors."""
        result = subprocess.run(
            [sys.executable, VALIDATE_PY, '--benchmark'],
            capture_output=True,
            text=True,
            cwd=VALIDATOR_DIR,
            timeout=120  # Allow up to 2 minutes for the benchmark
        )

        assert result.returncode == 0, (
            f"Benchmark failed with return code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_benchmark_validates_all_200_documents(self):
        """The benchmark must validate all 200 documents."""
        result = subprocess.run(
            [sys.executable, VALIDATE_PY, '--benchmark'],
            capture_output=True,
            text=True,
            cwd=VALIDATOR_DIR,
            timeout=120
        )

        output = result.stdout + result.stderr

        # Look for the document count in the output
        # Expected format: "Validated N documents in X.XXs (Y.Y docs/sec)"
        match = re.search(r'[Vv]alidat\w*\s+(\d+)\s+documents?', output)

        if match:
            doc_count = int(match.group(1))
            assert doc_count >= 200, (
                f"Benchmark only validated {doc_count} documents. "
                "All 200 test documents must be validated."
            )
        else:
            # If we can't find the count, check that at least 200 is mentioned
            assert '200' in output or result.returncode == 0, (
                f"Could not verify that 200 documents were validated.\n"
                f"Output: {output}"
            )

    def test_benchmark_achieves_400_docs_per_second(self):
        """The benchmark must achieve at least 400 docs/sec throughput."""
        result = subprocess.run(
            [sys.executable, VALIDATE_PY, '--benchmark'],
            capture_output=True,
            text=True,
            cwd=VALIDATOR_DIR,
            timeout=120
        )

        output = result.stdout + result.stderr

        # Expected format: "Validated N documents in X.XXs (Y.Y docs/sec)"
        # Try multiple patterns to find the throughput
        patterns = [
            r'(\d+\.?\d*)\s*docs?/s(?:ec)?',  # "400.5 docs/sec" or "400 docs/s"
            r'(\d+\.?\d*)\s*documents?/s(?:ec)?',  # "400.5 documents/sec"
            r'\((\d+\.?\d*)\s*docs?/s',  # "(400.5 docs/s"
            r'throughput[:\s]+(\d+\.?\d*)',  # "throughput: 400.5"
            r'(\d+\.?\d*)\s*validations?/s(?:ec)?',  # "400 validations/sec"
        ]

        throughput = None
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                throughput = float(match.group(1))
                break

        # If no explicit throughput found, try to calculate from time
        if throughput is None:
            time_match = re.search(r'(\d+)\s+documents?\s+in\s+(\d+\.?\d*)\s*s', output, re.IGNORECASE)
            if time_match:
                docs = int(time_match.group(1))
                seconds = float(time_match.group(2))
                if seconds > 0:
                    throughput = docs / seconds

        assert throughput is not None, (
            f"Could not find throughput in benchmark output.\n"
            f"Expected format like 'Validated N documents in X.XXs (Y.Y docs/sec)'\n"
            f"Output: {output}"
        )

        assert throughput >= 400, (
            f"Benchmark throughput is {throughput:.1f} docs/sec, "
            f"but must be at least 400 docs/sec.\n"
            f"Output: {output}"
        )

    def test_no_validation_errors(self):
        """The benchmark must complete without validation errors."""
        result = subprocess.run(
            [sys.executable, VALIDATE_PY, '--benchmark'],
            capture_output=True,
            text=True,
            cwd=VALIDATOR_DIR,
            timeout=120
        )

        output = (result.stdout + result.stderr).lower()

        # Check for common error indicators
        error_indicators = [
            'validationerror',
            'validation failed',
            'invalid',
            'schema error',
            'failed to validate',
        ]

        for indicator in error_indicators:
            # Allow "0 errors" or "no errors" type messages
            if indicator in output:
                # Make sure it's not a "0 errors" type message
                context_match = re.search(rf'(\d+)\s*{re.escape(indicator)}', output)
                if context_match and int(context_match.group(1)) > 0:
                    pytest.fail(
                        f"Validation errors detected in benchmark output.\n"
                        f"Output: {result.stdout + result.stderr}"
                    )


class TestJsonschemaStillUsed:
    """Verify jsonschema library is actually being used, not stubbed."""

    def test_jsonschema_import_works(self):
        """Verify jsonschema can still be imported."""
        result = subprocess.run(
            [sys.executable, '-c', 'from jsonschema import Draft7Validator; print("OK")'],
            capture_output=True,
            text=True,
            cwd=VALIDATOR_DIR
        )
        assert result.returncode == 0 and 'OK' in result.stdout, (
            "jsonschema.Draft7Validator must still be available."
        )

    def test_grep_draft7validator_count(self):
        """grep -c 'Draft7Validator' validate.py must be >= 1."""
        result = subprocess.run(
            ['grep', '-c', 'Draft7Validator', VALIDATE_PY],
            capture_output=True,
            text=True
        )

        # grep returns 0 if found, 1 if not found
        if result.returncode == 0:
            count = int(result.stdout.strip())
        else:
            count = 0

        assert count >= 1, (
            f"grep -c 'Draft7Validator' validate.py returned {count}. "
            "The script must still use Draft7Validator (count >= 1 required)."
        )


class TestNotCheating:
    """Tests to ensure the fix is legitimate, not a shortcut."""

    def test_testdata_not_reduced(self):
        """Cannot reduce the test set - all 200 documents must exist."""
        json_files = [f for f in os.listdir(TESTDATA_DIR) if f.endswith('.json')]
        assert len(json_files) >= 200, (
            f"Test data has been reduced to {len(json_files)} files. "
            "All 200 original test documents must remain."
        )

    def test_schemas_not_reduced(self):
        """Cannot reduce the schema set."""
        schema_files = [f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.json')]
        assert len(schema_files) >= 50, (
            f"Schemas have been reduced to {len(schema_files)} files. "
            "All 50 original schema files must remain."
        )

    def test_not_just_returning_true(self):
        """The validator cannot just return True without actual validation."""
        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        # Check that validate is actually called somewhere
        has_validate_call = '.validate(' in content or '.is_valid(' in content

        # Also check we're not just doing "return True" everywhere
        suspicious_patterns = [
            'def validate_document',
            'return True',
        ]

        # Count return True statements - having some is fine, but not as the only logic
        return_true_count = content.count('return True')

        # This is a heuristic check - if there are many "return True" and no validate calls,
        # it's suspicious
        if return_true_count > 5 and not has_validate_call:
            pytest.fail(
                "Suspicious code pattern: many 'return True' statements without "
                "actual validation calls. The validator must perform real validation."
            )
