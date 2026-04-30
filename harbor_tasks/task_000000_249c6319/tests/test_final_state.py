# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the ETL bug fix task.
"""

import pytest
import os
import json
import subprocess
import csv
import re


# Base paths
ETL_DIR = "/home/user/etl"
TRANSFORM_SCRIPT = os.path.join(ETL_DIR, "transform.py")
INPUT_JSON = os.path.join(ETL_DIR, "input/transactions.json")
OUTPUT_DIR = os.path.join(ETL_DIR, "output")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "transactions.csv")
LIB_DIR = os.path.join(ETL_DIR, "lib")
PARSERS_PY = os.path.join(LIB_DIR, "parsers.py")


def parse_amount_from_string(amount_str):
    """Helper to parse amount strings like '$1,234.56' or '€890.00' to float."""
    # Remove currency symbols and commas
    cleaned = re.sub(r'[^\d.]', '', amount_str)
    return float(cleaned)


def load_input_json():
    """Load and return the input JSON data."""
    with open(INPUT_JSON, 'r') as f:
        return json.load(f)


def load_output_csv():
    """Load and return the output CSV data as a list of dicts."""
    with open(OUTPUT_CSV, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


class TestScriptExecution:
    """Test that the transform script runs correctly after the fix."""

    def test_script_exits_zero(self):
        """Running the transform script should exit with code 0."""
        result = subprocess.run(
            ['python3', TRANSFORM_SCRIPT],
            cwd=ETL_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Transform script should exit 0, got {result.returncode}. Stderr: {result.stderr}"


class TestOutputCSVExists:
    """Test that the output CSV file exists and has correct structure."""

    def test_output_csv_exists(self):
        """Output CSV file should exist."""
        assert os.path.isfile(OUTPUT_CSV), \
            f"Output CSV file {OUTPUT_CSV} does not exist"

    def test_output_csv_has_248_lines(self):
        """Output CSV should have exactly 248 lines (1 header + 247 data rows)."""
        with open(OUTPUT_CSV, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 248, \
            f"Output CSV should have exactly 248 lines (1 header + 247 data rows), found {len(lines)}"

    def test_output_csv_has_correct_header(self):
        """Output CSV should have the correct column headers."""
        with open(OUTPUT_CSV, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)

        expected_columns = ['id', 'date', 'amount', 'currency', 'department', 'description']
        assert header == expected_columns, \
            f"CSV header should be {expected_columns}, got {header}"


class TestAllTransactionsPresent:
    """Test that all transactions from JSON are present in CSV."""

    def test_csv_has_247_data_rows(self):
        """CSV should have exactly 247 data rows."""
        csv_data = load_output_csv()
        assert len(csv_data) == 247, \
            f"CSV should have 247 data rows, found {len(csv_data)}"

    def test_all_transaction_ids_present(self):
        """Every transaction ID from JSON should appear exactly once in CSV."""
        json_data = load_input_json()
        csv_data = load_output_csv()

        json_ids = set(t['id'] for t in json_data)
        csv_ids = [row['id'] for row in csv_data]
        csv_ids_set = set(csv_ids)

        # Check all JSON IDs are in CSV
        missing_ids = json_ids - csv_ids_set
        assert not missing_ids, \
            f"Missing transaction IDs in CSV: {missing_ids}"

        # Check no extra IDs in CSV
        extra_ids = csv_ids_set - json_ids
        assert not extra_ids, \
            f"Extra transaction IDs in CSV not in JSON: {extra_ids}"

        # Check each ID appears exactly once
        assert len(csv_ids) == len(csv_ids_set), \
            f"Some transaction IDs appear more than once in CSV"

    def test_eur_transactions_present(self):
        """All 41 EUR transactions should be present in the CSV."""
        json_data = load_input_json()
        csv_data = load_output_csv()

        eur_ids_json = set(t['id'] for t in json_data if t['currency'] == 'EUR')
        csv_ids = set(row['id'] for row in csv_data)

        missing_eur = eur_ids_json - csv_ids
        assert not missing_eur, \
            f"Missing EUR transaction IDs: {missing_eur}"

        # Also verify count
        eur_in_csv = sum(1 for row in csv_data if row['currency'] == 'EUR')
        assert eur_in_csv == 41, \
            f"Should have 41 EUR transactions in CSV, found {eur_in_csv}"


class TestAmountValues:
    """Test that amount values are correctly parsed and formatted."""

    def test_amounts_are_numeric(self):
        """Amount column should contain numeric values (no currency symbols)."""
        csv_data = load_output_csv()

        for row in csv_data:
            amount_str = row['amount']
            # Should not contain currency symbols
            assert '$' not in amount_str, \
                f"Amount '{amount_str}' for ID {row['id']} should not contain $"
            assert '€' not in amount_str, \
                f"Amount '{amount_str}' for ID {row['id']} should not contain €"
            assert '£' not in amount_str, \
                f"Amount '{amount_str}' for ID {row['id']} should not contain £"

            # Should be parseable as float
            try:
                float(amount_str)
            except ValueError:
                pytest.fail(f"Amount '{amount_str}' for ID {row['id']} is not a valid number")

    def test_no_euro_symbols_in_csv(self):
        """CSV should not contain any euro symbols."""
        with open(OUTPUT_CSV, 'r') as f:
            content = f.read()

        euro_count = content.count('€')
        assert euro_count == 0, \
            f"CSV should not contain € symbols, found {euro_count}"

    def test_amounts_match_source(self):
        """CSV amounts should match the parsed amounts from JSON."""
        json_data = load_input_json()
        csv_data = load_output_csv()

        # Create lookup by ID
        json_by_id = {t['id']: t for t in json_data}

        for row in csv_data:
            tid = row['id']
            json_amount_str = json_by_id[tid]['amount']
            expected_amount = parse_amount_from_string(json_amount_str)
            actual_amount = float(row['amount'])

            assert abs(actual_amount - expected_amount) < 0.01, \
                f"Amount mismatch for ID {tid}: expected {expected_amount}, got {actual_amount} (source: {json_amount_str})"

    def test_total_sum_matches(self):
        """Sum of all amounts in CSV should equal sum from JSON (within tolerance)."""
        json_data = load_input_json()
        csv_data = load_output_csv()

        json_total = sum(parse_amount_from_string(t['amount']) for t in json_data)
        csv_total = sum(float(row['amount']) for row in csv_data)

        assert abs(csv_total - json_total) < 0.01, \
            f"Total sum mismatch: JSON total={json_total}, CSV total={csv_total}, diff={abs(csv_total - json_total)}"


class TestInputDataUnmodified:
    """Test that input data was not modified."""

    def test_input_json_has_247_transactions(self):
        """Input JSON should still have 247 transactions."""
        json_data = load_input_json()
        assert len(json_data) == 247, \
            f"Input JSON should have 247 transactions, found {len(json_data)}"

    def test_input_json_still_has_currency_symbols(self):
        """Input JSON amounts should still have currency symbols (not modified)."""
        json_data = load_input_json()

        usd_with_symbol = sum(1 for t in json_data if '$' in t['amount'])
        eur_with_symbol = sum(1 for t in json_data if '€' in t['amount'])

        assert usd_with_symbol > 0, \
            "Input JSON should still have USD amounts with $ symbol"
        assert eur_with_symbol > 0, \
            "Input JSON should still have EUR amounts with € symbol"


class TestCSVColumnOrder:
    """Test that CSV column order is preserved."""

    def test_column_order_preserved(self):
        """CSV columns should be in order: id,date,amount,currency,department,description."""
        with open(OUTPUT_CSV, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)

        expected_order = ['id', 'date', 'amount', 'currency', 'department', 'description']
        assert header == expected_order, \
            f"CSV column order should be {expected_order}, got {header}"


class TestParsersFix:
    """Test that the parsers module fix handles currency symbols generically."""

    def test_parsers_handles_multiple_currencies(self):
        """The parse_amount function should handle arbitrary currency symbols."""
        # Import the parsers module dynamically
        import sys
        sys.path.insert(0, LIB_DIR)

        try:
            # Reload to get the fixed version
            if 'parsers' in sys.modules:
                del sys.modules['parsers']

            import parsers

            # Test various currency formats
            test_cases = [
                ("$1,234.56", 1234.56),
                ("€890.00", 890.00),
                ("£500.00", 500.00),
                ("$100", 100.0),
                ("€50.5", 50.5),
                ("1000.00", 1000.0),  # No symbol
                ("$1,000,000.00", 1000000.0),
            ]

            for input_str, expected in test_cases:
                try:
                    result = parsers.parse_amount(input_str)
                    assert abs(result - expected) < 0.01, \
                        f"parse_amount('{input_str}') should return {expected}, got {result}"
                except Exception as e:
                    pytest.fail(f"parse_amount('{input_str}') raised {type(e).__name__}: {e}")

        finally:
            sys.path.remove(LIB_DIR)
            if 'parsers' in sys.modules:
                del sys.modules['parsers']

    def test_parsers_handles_pound_symbol(self):
        """Specifically test that £ symbol is handled (anti-shortcut guard)."""
        import sys
        sys.path.insert(0, LIB_DIR)

        try:
            if 'parsers' in sys.modules:
                del sys.modules['parsers']

            import parsers

            # Test pound symbol specifically
            result = parsers.parse_amount("£500.00")
            assert abs(result - 500.0) < 0.01, \
                f"parse_amount('£500.00') should return 500.0, got {result}. " \
                f"Fix must handle arbitrary currency symbols, not just $ and €"

        except Exception as e:
            pytest.fail(
                f"parse_amount('£500.00') failed with {type(e).__name__}: {e}. "
                f"The fix must handle arbitrary currency symbols generically, not just $ and €"
            )

        finally:
            sys.path.remove(LIB_DIR)
            if 'parsers' in sys.modules:
                del sys.modules['parsers']


class TestDataIntegrity:
    """Test overall data integrity between JSON and CSV."""

    def test_all_fields_transferred(self):
        """All fields from JSON should be present in CSV for each transaction."""
        json_data = load_input_json()
        csv_data = load_output_csv()

        json_by_id = {t['id']: t for t in json_data}

        for row in csv_data:
            tid = row['id']
            json_record = json_by_id[tid]

            # Check date matches
            assert row['date'] == json_record['date'], \
                f"Date mismatch for ID {tid}"

            # Check currency matches
            assert row['currency'] == json_record['currency'], \
                f"Currency mismatch for ID {tid}"

            # Check department matches
            assert row['department'] == json_record['department'], \
                f"Department mismatch for ID {tid}"

            # Check description matches
            assert row['description'] == json_record['description'], \
                f"Description mismatch for ID {tid}"
