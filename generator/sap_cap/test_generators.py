"""
SAP CAP test generation for initial state and final state verification.
"""
from __future__ import annotations

from typing import Dict, Any


def generate_cap_initial_test(task_data: Dict[str, Any]) -> str:
    """
    Generate initial state test for SAP CAP task.

    Verifies the environment is properly set up with Node.js, CDS tools, etc.

    Args:
        task_data: Task metadata dictionary

    Returns:
        Python test code as string
    """
    return """import subprocess
import sys
from pathlib import Path


def test_node_installed():
    \"\"\"Verify Node.js is installed.\"\"\"
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "Node.js is not installed"
    version = result.stdout.strip()
    major_version = int(version.lstrip('v').split('.')[0])
    assert major_version >= 20, f"Node.js version must be >= 20, got {version}"


def test_npm_installed():
    \"\"\"Verify npm is installed.\"\"\"
    result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "npm is not installed"


def test_cds_installed():
    \"\"\"Verify SAP CDS tools are installed.\"\"\"
    result = subprocess.run(["cds", "version"], capture_output=True, text=True)
    assert result.returncode == 0, "CDS tools are not installed"
    assert "@sap/cds" in result.stdout, "CDS installation seems incomplete"


def test_sqlite3_available():
    \"\"\"Verify SQLite3 is available.\"\"\"
    result = subprocess.run(["sqlite3", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "SQLite3 is not installed"


def test_working_directory():
    \"\"\"Verify we are in /home/user directory.\"\"\"
    cwd = Path.cwd()
    assert cwd == Path("/home/user"), f"Working directory should be /home/user, got {cwd}"
"""


def generate_cap_final_test(task_data: Dict[str, Any]) -> str:
    """
    Generate final state test for SAP CAP task.

    Verifies the task requirements are met (files created, CDS compiles, etc.)

    Args:
        task_data: Task metadata including category, required_files, entities, etc.

    Returns:
        Python test code as string
    """
    category = task_data.get("category", "data_modeling")
    required_files = task_data.get("required_files", ["db/schema.cds"])
    entities = task_data.get("entities", [])

    # Build test code based on category
    test_code = """import subprocess
import sys
from pathlib import Path


"""

    # Add file existence tests
    for filepath in required_files:
        test_name = f"test_{filepath.replace('/', '_').replace('.', '_')}_exists"
        test_code += f"""def {test_name}():
    \"\"\"Verify {filepath} exists.\"\"\"
    assert Path("{filepath}").exists(), "{filepath} does not exist"


"""

    # Add CDS compilation test if schema file is required
    if any("schema.cds" in f for f in required_files):
        test_code += """def test_cds_schema_compiles():
    \"\"\"Verify CDS schema compiles without errors.\"\"\"
    result = subprocess.run(
        ["cds", "compile", "db/schema.cds"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CDS compilation failed: {result.stderr}"


"""

        # Add entity definition tests
        if entities:
            for entity in entities:
                test_code += f"""def test_entity_{entity.lower()}_defined():
    \"\"\"Verify {entity} entity is defined in schema.\"\"\"
    schema_content = Path("db/schema.cds").read_text()
    assert "entity {entity}" in schema_content or "entity {entity.lower()}" in schema_content.lower(), \\
        f"{entity} entity not found in schema"


"""

    # Add service tests if service file is required
    if any("service.cds" in f for f in required_files):
        test_code += """def test_service_compiles():
    \"\"\"Verify CDS service compiles without errors.\"\"\"
    result = subprocess.run(
        ["cds", "compile", "srv"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Service compilation failed: {result.stderr}"


def test_service_metadata_generation():
    \"\"\"Verify service can generate OData metadata.\"\"\"
    result = subprocess.run(
        ["cds", "compile", "srv", "--to", "edmx"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Metadata generation failed: {result.stderr}"
    assert "<edmx:Edmx" in result.stdout, "Invalid OData metadata generated"


"""

    # Add database tests if DB operations are involved
    if category == "database_operations" or "sqlite.db" in required_files:
        test_code += """def test_database_exists():
    \"\"\"Verify SQLite database file exists.\"\"\"
    assert Path("sqlite.db").exists(), "Database file sqlite.db does not exist"


def test_database_schema():
    \"\"\"Verify database has tables from schema.\"\"\"
    result = subprocess.run(
        ["sqlite3", "sqlite.db", ".tables"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "Failed to query database tables"
    # At least one table should exist
    assert len(result.stdout.strip()) > 0, "Database has no tables"


"""

    return test_code


def generate_cap_test_suite(task_data: Dict[str, Any]) -> tuple[str, str]:
    """
    Generate complete test suite (initial + final) for SAP CAP task.

    Args:
        task_data: Task metadata dictionary

    Returns:
        Tuple of (initial_test_code, final_test_code)
    """
    initial_test = generate_cap_initial_test(task_data)
    final_test = generate_cap_final_test(task_data)
    return initial_test, final_test