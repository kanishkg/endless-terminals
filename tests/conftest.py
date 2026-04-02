"""
Test configuration and fixtures for endless-terminals tests.
"""
import pytest


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "task_id": "001",
        "task_description": "Sample task for unit testing",
        "category": "test",
        "complexity": "simple",
        "required_files": ["test.py"],
        "success_criteria": ["File exists", "Code runs"],
    }


@pytest.fixture
def cap_task_data():
    """Sample CAP task data for testing."""
    return {
        "task_id": "cap_001",
        "task_description": "Create a CDS model for a bookshop",
        "category": "data_modeling",
        "complexity": "simple",
        "domain": "bookshop",
        "required_files": ["db/schema.cds"],
        "entities": ["Books", "Authors"],
        "success_criteria": [
            "db/schema.cds exists",
            "Entities are defined",
            "CDS compiles",
        ],
    }
