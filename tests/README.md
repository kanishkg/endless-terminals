# Test Suite for Endless Terminals

This directory contains comprehensive unit tests for the Endless Terminals project, focusing on Harbor integration and SAP CAP task generation.

## Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_harbor_conversion.py      # Tests for Harbor task conversion
├── test_sap_cap_generation.py     # Tests for SAP CAP task generation
└── README.md                      # This file
```

## Running Tests

### Install test dependencies

```bash
cd endless-terminals-main
uv sync --extra harbor
uv pip install pytest pytest-cov pytest-mock
```

### Run all tests

```bash
pytest tests/
```

### Run specific test file

```bash
pytest tests/test_harbor_conversion.py
pytest tests/test_sap_cap_generation.py
```

### Run with coverage

```bash
pytest tests/ --cov=generator --cov-report=html
```

### Run with verbose output

```bash
pytest tests/ -v
```

## Test Coverage

### Harbor Conversion Tests (`test_harbor_conversion.py`)

- **TestLoadTaskJson**: Loading and parsing task.json files
- **TestCreateInstructionMd**: Generating Harbor instruction.md files
- **TestGetTaskDirectories**: Task directory discovery
- **TestConvertTaskToHarbor**: End-to-end conversion workflow
- **TestIntegrationScenarios**: Batch conversion scenarios

### SAP CAP Generation Tests (`test_sap_cap_generation.py`)

- **TestCAPTaskCategories**: Task category definitions
- **TestGenerateCAPTask**: Task generation across categories and complexities
- **TestCAPInitialTestGeneration**: Initial environment test generation
- **TestCAPFinalTestGeneration**: Final verification test generation
- **TestCAPTestSuite**: Complete test suite generation
- **TestCAPContainerSetup**: Container configuration generation
- **TestIntegrationScenarios**: End-to-end workflows
- **TestEdgeCases**: Error handling and edge cases

## Test Fixtures

### `sample_task_data`
Generic task data for testing basic functionality.

### `cap_task_data`
SAP CAP-specific task data for testing CAP generation.

### `tmp_path` (pytest built-in)
Temporary directory for file system tests.

## Writing New Tests

Follow these conventions:

1. **Class-based organization**: Group related tests in classes
2. **Descriptive names**: `test_<what>_<when>_<expected>`
3. **Use fixtures**: Reuse common test data
4. **Mock external calls**: Use `pytest-mock` for LLM calls, API calls, etc.
5. **Assert clearly**: Include descriptive assertion messages

Example:

```python
def test_generate_task_with_specific_domain():
    """Test generating task with specific business domain."""
    task = generate_cap_task("data_modeling", domain="bookshop")

    assert task["domain"] == "bookshop", \
        f"Expected domain 'bookshop', got '{task['domain']}'"
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines without external dependencies (mocked).

## Test Philosophy

- **Unit tests**: Fast, isolated, no external dependencies
- **Integration tests**: Test component interactions
- **Mocking**: Mock LLM calls, file I/O where appropriate
- **Fixtures**: Reuse common setup code
- **Coverage**: Aim for >80% coverage on new code
