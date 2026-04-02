#!/bin/bash
# Run tests for Endless Terminals project

set -e

echo "============================================"
echo "  Endless Terminals Test Runner"
echo "============================================"
echo ""

# Default values
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""
MARKER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --test|-t)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --marker|-m)
            MARKER="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage          Run with coverage report"
            echo "  -v, --verbose           Verbose output"
            echo "  -t, --test FILE         Run specific test file"
            echo "  -m, --marker MARKER     Run tests with specific marker"
            echo "                          (e.g., harbor, cap, unit, integration)"
            echo "  -h, --help              Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all tests"
            echo "  $0 --coverage                         # Run with coverage"
            echo "  $0 --test test_harbor_conversion.py  # Run specific file"
            echo "  $0 --marker harbor                    # Run Harbor tests only"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed"
    echo "Install with: uv pip install pytest pytest-cov pytest-mock"
    exit 1
fi

# Build pytest command
PYTEST_CMD="pytest"

if [[ -n "$SPECIFIC_TEST" ]]; then
    PYTEST_CMD="$PYTEST_CMD tests/$SPECIFIC_TEST"
else
    PYTEST_CMD="$PYTEST_CMD tests/"
fi

if [[ "$VERBOSE" == "true" ]]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [[ "$COVERAGE" == "true" ]]; then
    PYTEST_CMD="$PYTEST_CMD --cov=generator --cov-report=term-missing --cov-report=html"
fi

if [[ -n "$MARKER" ]]; then
    PYTEST_CMD="$PYTEST_CMD -m $MARKER"
fi

echo "Running: $PYTEST_CMD"
echo ""

# Run tests
$PYTEST_CMD

# Show coverage report location if generated
if [[ "$COVERAGE" == "true" ]]; then
    echo ""
    echo "Coverage report generated: htmlcov/index.html"
    echo "Open with: open htmlcov/index.html"
fi
