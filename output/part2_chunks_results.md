# Harbor Run Results — Part 2 Chunks

**Date**: 2026-05-23
**Model**: claude-4.5-sonnet
**Task set**: harbor_tasks_part2_2-[2,3,4]

| Job | Attempts | Concurrent | Total Trials | Errored | Passed | Failed | Score | Runtime |
|-----|----------|------------|-------------|---------|--------|--------|-------|---------|
| 2-2 | 8 | 10 | 10760 | 7987 | 1077 | 1846 | 0.1001 | 21.4h |
| 2-3 | 4 | 10 | 5380 | 3954 | 474 | 997 | 0.0881 | 10.4h |
| 2-4 | 8 | 4 | 10760 | 8017 | 783 | 2105 | 0.0728 | 48.8h |

## Notes

- ~74% of errors are due to heredoc Dockerfile generation bug (bash `<< 'EOF'` syntax parsed as Dockerfile instructions)
- 2-3 ran half the trials due to `--n-attempts 4` vs 8 for other jobs
- 2-2 achieved best score (0.1001) with 10 concurrent and 8 attempts
