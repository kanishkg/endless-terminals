"""
Unit tests for SAP CAP task generation functionality.

Tests the sap_cap module including task templates, test generation,
and container setup.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.sap_cap.task_templates import (
    CAP_TASK_CATEGORIES,
    generate_cap_task,
    get_all_cap_templates,
    DATA_MODELING_TEMPLATES,
    SERVICE_DEFINITION_TEMPLATES,
    DATABASE_OPERATIONS_TEMPLATES,
)
from generator.sap_cap.test_generators import (
    generate_cap_initial_test,
    generate_cap_final_test,
    generate_cap_test_suite,
)
from generator.sap_cap.container_setup import (
    get_cap_container_def,
    get_cap_dockerfile,
)


class TestCAPTaskCategories:
    """Test CAP task category definitions."""

    def test_categories_defined(self):
        """Test that task categories are properly defined."""
        assert len(CAP_TASK_CATEGORIES) > 0
        assert "data_modeling" in CAP_TASK_CATEGORIES
        assert "service_definition" in CAP_TASK_CATEGORIES
        assert "database_operations" in CAP_TASK_CATEGORIES

    def test_templates_available(self):
        """Test that templates exist for each category."""
        templates = get_all_cap_templates()
        assert len(templates) > 0

        # Check templates cover multiple categories
        categories_covered = {t.category for t in templates}
        assert "data_modeling" in categories_covered


class TestGenerateCAPTask:
    """Test CAP task generation."""

    def test_generate_data_modeling_simple(self):
        """Test generating simple data modeling task."""
        task = generate_cap_task("data_modeling", complexity="simple")

        assert task["category"] == "data_modeling"
        assert task["complexity"] == "simple"
        assert "task_description" in task
        assert len(task["task_description"]) > 0
        assert "required_files" in task
        assert "db/schema.cds" in task["required_files"]

    def test_generate_data_modeling_medium(self):
        """Test generating medium complexity data modeling task."""
        task = generate_cap_task("data_modeling", complexity="medium")

        assert task["category"] == "data_modeling"
        assert task["complexity"] == "medium"
        assert "entities" in task
        assert len(task["entities"]) >= 2
        assert "relationship" in task["task_description"].lower()

    def test_generate_data_modeling_complex(self):
        """Test generating complex data modeling task."""
        task = generate_cap_task("data_modeling", complexity="complex")

        assert task["category"] == "data_modeling"
        assert task["complexity"] == "complex"
        assert "managed" in task["task_description"].lower() or "annotation" in task["task_description"].lower()

    def test_generate_service_definition(self):
        """Test generating service definition task."""
        task = generate_cap_task("service_definition", complexity="simple")

        assert task["category"] == "service_definition"
        assert "srv/catalog-service.cds" in task["required_files"]
        assert "service" in task["task_description"].lower()

    def test_generate_database_operations(self):
        """Test generating database operations task."""
        task = generate_cap_task("database_operations", complexity="medium")

        assert task["category"] == "database_operations"
        assert "database" in task["task_description"].lower() or "data" in task["task_description"].lower()
        assert "success_criteria" in task
        assert len(task["success_criteria"]) > 0

    def test_generate_with_specific_domain(self):
        """Test generating task with specific business domain."""
        task = generate_cap_task("data_modeling", complexity="simple", domain="bookshop")

        assert task["domain"] == "bookshop"
        assert "bookshop" in task["task_description"].lower()

    def test_generate_invalid_category(self):
        """Test generating task with invalid category."""
        with pytest.raises(ValueError, match="Unknown category"):
            generate_cap_task("invalid_category")

    def test_task_has_required_fields(self):
        """Test that generated task has all required fields."""
        task = generate_cap_task("data_modeling", complexity="simple")

        required_fields = [
            "task_description",
            "category",
            "complexity",
            "domain",
            "required_files",
            "success_criteria",
            "hints",
            "focus_areas",
        ]

        for field in required_fields:
            assert field in task, f"Missing required field: {field}"

    def test_task_description_not_empty(self):
        """Test that task descriptions are not empty."""
        for category in ["data_modeling", "service_definition", "database_operations"]:
            for complexity in ["simple", "medium", "complex"]:
                try:
                    task = generate_cap_task(category, complexity=complexity)
                    assert len(task["task_description"]) > 50, \
                        f"Task description too short for {category}/{complexity}"
                except ValueError:
                    # Skip if template doesn't exist for this combination
                    pass


class TestCAPInitialTestGeneration:
    """Test initial state test generation."""

    def test_generate_initial_test(self):
        """Test generating initial state test."""
        task_data = {
            "category": "data_modeling",
            "complexity": "simple",
        }

        test_code = generate_cap_initial_test(task_data)

        assert "def test_node_installed" in test_code
        assert "def test_npm_installed" in test_code
        assert "def test_cds_installed" in test_code
        assert "def test_sqlite3_available" in test_code
        assert "subprocess.run" in test_code

    def test_initial_test_checks_node_version(self):
        """Test that initial test validates Node.js version."""
        test_code = generate_cap_initial_test({})

        assert "major_version >= 20" in test_code
        assert "Node.js version must be" in test_code

    def test_initial_test_checks_working_directory(self):
        """Test that initial test validates working directory."""
        test_code = generate_cap_initial_test({})

        assert "/home/user" in test_code
        assert "def test_working_directory" in test_code


class TestCAPFinalTestGeneration:
    """Test final state test generation."""

    def test_generate_final_test_basic(self):
        """Test generating basic final state test."""
        task_data = {
            "category": "data_modeling",
            "required_files": ["db/schema.cds"],
            "entities": ["Books", "Authors"],
        }

        test_code = generate_cap_final_test(task_data)

        assert "def test_db_schema_cds_exists" in test_code
        assert "def test_cds_schema_compiles" in test_code
        assert "def test_entity_books_defined" in test_code
        assert "def test_entity_authors_defined" in test_code

    def test_generate_final_test_service(self):
        """Test generating final test for service tasks."""
        task_data = {
            "category": "service_definition",
            "required_files": ["srv/catalog-service.cds", "db/schema.cds"],
            "entities": [],
        }

        test_code = generate_cap_final_test(task_data)

        assert "def test_service_compiles" in test_code
        assert "def test_service_metadata_generation" in test_code
        assert "edmx" in test_code.lower()

    def test_generate_final_test_database(self):
        """Test generating final test for database tasks."""
        task_data = {
            "category": "database_operations",
            "required_files": ["sqlite.db", "db/schema.cds"],
            "entities": [],
        }

        test_code = generate_cap_final_test(task_data)

        assert "def test_database_exists" in test_code
        assert "def test_database_schema" in test_code
        assert "sqlite3" in test_code

    def test_final_test_no_duplicates(self):
        """Test that generated tests don't have duplicate function names."""
        task_data = {
            "category": "data_modeling",
            "required_files": ["db/schema.cds", "srv/service.cds"],
            "entities": ["Books", "Books"],  # Duplicate entity
        }

        test_code = generate_cap_final_test(task_data)

        # Count occurrences of test function definitions
        lines = test_code.split("\n")
        test_functions = [line for line in lines if line.startswith("def test_")]

        # Should not have duplicate function names
        function_names = [line.split("(")[0] for line in test_functions]
        assert len(function_names) == len(set(function_names)), \
            f"Duplicate test functions found: {function_names}"


class TestCAPTestSuite:
    """Test complete test suite generation."""

    def test_generate_complete_suite(self):
        """Test generating complete test suite."""
        task_data = {
            "category": "data_modeling",
            "complexity": "medium",
            "required_files": ["db/schema.cds"],
            "entities": ["Books", "Authors"],
        }

        initial_test, final_test = generate_cap_test_suite(task_data)

        assert len(initial_test) > 0
        assert len(final_test) > 0
        assert "def test_" in initial_test
        assert "def test_" in final_test
        assert initial_test != final_test


class TestCAPContainerSetup:
    """Test container setup generation."""

    def test_get_container_def(self):
        """Test getting Apptainer container definition."""
        container_def = get_cap_container_def()

        assert "Bootstrap: docker" in container_def
        assert "From: ubuntu:22.04" in container_def
        assert "nodejs" in container_def.lower()
        assert "@sap/cds-dk" in container_def
        assert "useradd" in container_def

    def test_container_def_has_node_20(self):
        """Test that container definition installs Node.js 20."""
        container_def = get_cap_container_def()

        assert "setup_20.x" in container_def

    def test_get_dockerfile(self):
        """Test getting Dockerfile."""
        dockerfile = get_cap_dockerfile()

        assert "FROM ubuntu:22.04" in dockerfile
        assert "nodejs" in dockerfile.lower()
        assert "@sap/cds-dk" in dockerfile
        assert "WORKDIR /home/user" in dockerfile
        assert "USER user" in dockerfile

    def test_dockerfile_multi_stage_not_required(self):
        """Test that Dockerfile is single-stage (for simplicity)."""
        dockerfile = get_cap_dockerfile()

        # Count FROM statements (should be 1 for single-stage)
        from_count = dockerfile.count("FROM ")
        assert from_count == 1


class TestIntegrationScenarios:
    """Integration tests for complete CAP task generation workflow."""

    def test_end_to_end_task_generation(self):
        """Test complete workflow: generate task + tests + container."""
        # Generate task
        task = generate_cap_task("data_modeling", complexity="simple", domain="bookshop")

        # Generate tests
        initial_test, final_test = generate_cap_test_suite(task)

        # Get container setup
        container_def = get_cap_container_def()

        # Verify all components are present
        assert len(task["task_description"]) > 0
        assert len(initial_test) > 0
        assert len(final_test) > 0
        assert len(container_def) > 0

        # Verify consistency
        for required_file in task["required_files"]:
            # Final test should check for required files
            assert required_file.replace("/", "_").replace(".", "_") in final_test

    def test_generate_multiple_tasks_different_domains(self):
        """Test generating tasks across different business domains."""
        domains = ["bookshop", "inventory", "order management"]
        tasks = []

        for domain in domains:
            task = generate_cap_task("data_modeling", complexity="medium", domain=domain)
            tasks.append(task)

        # All tasks should be different
        descriptions = [t["task_description"] for t in tasks]
        assert len(set(descriptions)) == len(descriptions)

        # All should have valid structure
        for task in tasks:
            assert task["domain"] in domains
            assert len(task["required_files"]) > 0
            assert len(task["entities"]) > 0

    def test_complexity_progression(self):
        """Test that complexity levels produce progressively complex tasks."""
        simple = generate_cap_task("data_modeling", complexity="simple", domain="bookshop")
        medium = generate_cap_task("data_modeling", complexity="medium", domain="bookshop")
        complex_task = generate_cap_task("data_modeling", complexity="complex", domain="bookshop")

        # Simple should be shorter and have fewer requirements
        assert len(simple["task_description"]) <= len(medium["task_description"])
        assert len(simple["success_criteria"]) <= len(complex_task["success_criteria"])

        # Complex should mention advanced features
        complex_desc = complex_task["task_description"].lower()
        assert any(keyword in complex_desc for keyword in ["managed", "annotation", "many-to-many"])


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_task_data(self):
        """Test handling empty task data."""
        initial_test = generate_cap_initial_test({})
        assert len(initial_test) > 0

        final_test = generate_cap_final_test({})
        assert len(final_test) > 0

    def test_task_with_no_entities(self):
        """Test generating final test with no entities."""
        task_data = {
            "category": "file_management",
            "required_files": ["package.json"],
            "entities": [],
        }

        test_code = generate_cap_final_test(task_data)
        assert "def test_" in test_code
        # Should not crash, should generate file existence tests

    def test_task_with_many_files(self):
        """Test generating tests for task with many required files."""
        task_data = {
            "category": "file_management",
            "required_files": [
                "db/schema.cds",
                "srv/service1.cds",
                "srv/service2.cds",
                "package.json",
                "README.md",
            ],
            "entities": [],
        }

        test_code = generate_cap_final_test(task_data)

        # Should have test for each file
        for filepath in task_data["required_files"]:
            test_name = filepath.replace("/", "_").replace(".", "_")
            assert f"def test_{test_name}_exists" in test_code
