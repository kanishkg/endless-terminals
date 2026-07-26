#!/usr/bin/env bash
# check_final_tests_initial_state.sh
#
# For each task in harbor_tasks/, build the Docker image from the initial state,
# then run the final-state tests WITHOUT applying any solution. If the final tests
# pass in the initial state, the task is trivially "solved" without any work.
#
# Usage:
#   ./scripts/check_final_tests_initial_state.sh [--tasks-dir DIR] [--output FILE] [--parallel N] [--timeout SECS]
#
# Output: CSV file with columns:
#   task_name, docker_build_success, final_tests_exit_code, final_tests_passed, num_passed, num_failed, num_errors, details

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TASKS_DIR="${REPO_ROOT}/harbor_tasks"
OUTPUT_FILE="${REPO_ROOT}/final_tests_initial_state_results.csv"
PARALLEL=4
BUILD_TIMEOUT=600
TEST_TIMEOUT=300

usage() {
    echo "Usage: $0 [--tasks-dir DIR] [--output FILE] [--parallel N] [--timeout SECS]"
    echo ""
    echo "Options:"
    echo "  --tasks-dir DIR    Directory containing task folders (default: harbor_tasks/)"
    echo "  --output FILE      Output CSV path (default: final_tests_initial_state_results.csv)"
    echo "  --parallel N       Max concurrent Docker builds (default: 4)"
    echo "  --timeout SECS     Test execution timeout in seconds (default: 300)"
    echo "  --help             Show this help"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tasks-dir) TASKS_DIR="$2"; shift 2 ;;
        --output) OUTPUT_FILE="$2"; shift 2 ;;
        --parallel) PARALLEL="$2"; shift 2 ;;
        --timeout) TEST_TIMEOUT="$2"; shift 2 ;;
        --help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ ! -d "$TASKS_DIR" ]]; then
    echo "ERROR: Tasks directory not found: $TASKS_DIR"
    exit 1
fi

echo "task_name,docker_build_success,final_tests_exit_code,final_tests_passed,num_passed,num_failed,num_errors,details" > "$OUTPUT_FILE"

check_task() {
    local task_dir="$1"
    local task_name
    task_name="$(basename "$task_dir")"

    local dockerfile="${task_dir}/environment/Dockerfile"
    local final_test="${task_dir}/tests/test_final_state.py"

    if [[ ! -f "$dockerfile" ]]; then
        echo "${task_name},false,-1,false,0,0,0,missing_dockerfile"
        return
    fi

    if [[ ! -f "$final_test" ]]; then
        echo "${task_name},false,-1,false,0,0,0,missing_final_test"
        return
    fi

    local image_tag="check-final-initial-${task_name}"
    local tmp_dir
    tmp_dir="$(mktemp -d)"

    cp "$dockerfile" "${tmp_dir}/Dockerfile"
    cp "$final_test" "${tmp_dir}/test_final_state.py"

    # Build the Docker image
    local build_output
    build_output=$(docker build --network host --progress=plain \
        -t "$image_tag" \
        -f "${tmp_dir}/Dockerfile" \
        "$tmp_dir" 2>&1) || true

    if ! docker image inspect "$image_tag" &>/dev/null; then
        local err_snippet
        err_snippet=$(echo "$build_output" | tail -3 | tr '\n' ' ' | cut -c1-200)
        echo "${task_name},false,-1,false,0,0,0,build_failed: ${err_snippet}"
        rm -rf "$tmp_dir"
        return
    fi

    # Run final tests inside the container (in the initial state, no solution applied)
    local test_output
    local exit_code=0
    test_output=$(timeout "$TEST_TIMEOUT" docker run --rm \
        --memory 4g --memory-swap 4g \
        -v "${tmp_dir}:/mnt:ro" \
        "$image_tag" \
        bash -c "cp /mnt/test_final_state.py /home/user/ && cd /home/user && pytest -v test_final_state.py 2>&1" 2>&1) || exit_code=$?

    # Handle timeout
    if [[ "$exit_code" -eq 124 ]]; then
        echo "${task_name},true,124,false,0,0,0,test_timeout"
        docker rmi "$image_tag" &>/dev/null || true
        rm -rf "$tmp_dir"
        return
    fi

    # Parse pytest output for pass/fail counts from the summary line
    # e.g. "3 failed, 18 passed, 11 skipped in 0.10s"
    local num_passed=0
    local num_failed=0
    local num_errors=0

    local summary_line
    summary_line=$(echo "$test_output" | grep -E '=.*(passed|failed|error)' | tail -1 || echo "")

    num_passed=$(echo "$summary_line" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' | head -1 || echo "0")
    num_passed="${num_passed:-0}"

    num_failed=$(echo "$summary_line" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | head -1 || echo "0")
    num_failed="${num_failed:-0}"

    num_errors=$(echo "$summary_line" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+' | head -1 || echo "0")
    num_errors="${num_errors:-0}"

    local tests_passed="false"
    if [[ "$exit_code" -eq 0 ]]; then
        tests_passed="true"
    fi

    # Get the pytest summary line as detail
    local detail
    detail=$(echo "$summary_line" | tr ',' ';' | tr '\n' ' ' | cut -c1-200)
    detail="${detail//,/;}"

    echo "${task_name},true,${exit_code},${tests_passed},${num_passed},${num_failed},${num_errors},${detail}"

    # Cleanup
    docker rmi "$image_tag" &>/dev/null || true
    rm -rf "$tmp_dir"
}

export -f check_task
export TEST_TIMEOUT

# Collect all task directories
task_dirs=()
for task_dir in "${TASKS_DIR}"/task_*; do
    if [[ -d "$task_dir" ]]; then
        task_dirs+=("$task_dir")
    fi
done

total=${#task_dirs[@]}
echo "Found $total tasks in $TASKS_DIR"
echo "Output will be written to: $OUTPUT_FILE"
echo "Running with parallelism: $PARALLEL"
echo ""

completed=0
for task_dir in "${task_dirs[@]}"; do
    completed=$((completed + 1))
    task_name="$(basename "$task_dir")"
    echo "[$completed/$total] Checking: $task_name"
    result=$(check_task "$task_dir")
    echo "$result" >> "$OUTPUT_FILE"

    # Print status inline based on CSV fields
    build_ok=$(echo "$result" | cut -d',' -f2)
    final_passed=$(echo "$result" | cut -d',' -f4)

    if [[ "$build_ok" == "false" ]]; then
        echo "  Build failed or missing files"
    elif [[ "$final_passed" == "true" ]]; then
        echo "  *** FINAL TESTS PASS IN INITIAL STATE (trivially solved!) ***"
    else
        echo "  Final tests fail in initial state (expected)"
    fi
done

echo ""
echo "=== SUMMARY ==="
echo "Results written to: $OUTPUT_FILE"
echo ""

trivial_count=$(tail -n +2 "$OUTPUT_FILE" | awk -F',' '$4=="true"' | wc -l)
build_fail_count=$(tail -n +2 "$OUTPUT_FILE" | awk -F',' '$2=="false"' | wc -l)
expected_count=$(tail -n +2 "$OUTPUT_FILE" | awk -F',' '$2=="true" && $4=="false"' | wc -l)

echo "Total tasks: $total"
echo "Final tests PASS in initial state (TRIVIAL - no work needed): $trivial_count"
echo "Build failures: $build_fail_count"
echo "Final tests FAIL in initial state (expected/good): $expected_count"

if [[ "$trivial_count" -gt 0 ]]; then
    echo ""
    echo "=== TRIVIALLY SOLVED TASKS ==="
    tail -n +2 "$OUTPUT_FILE" | awk -F',' '$4=="true" {print $1}'
fi
