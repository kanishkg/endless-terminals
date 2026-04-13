You are a build engineer who needs to analyze a build artifact log to identify failed component builds. The log file is located at `/home/user/builds/artifact_build.log`.

This log file contains entries for various component builds. Each line in the log follows this format:
`[TIMESTAMP] [STATUS] component_name - message`

Where STATUS is either `SUCCESS` or `FAILED`.

Your task is to:

1. Extract all the failed component names from the log file
2. Count how many components failed in total
3. Create a summary report file at `/home/user/builds/failure_report.txt`

The failure report file must have the following exact format:
- First line: `FAILED_COMPONENTS_COUNT: X` (where X is the number of failed components)
- Second line: blank
- Third line and onwards: List each failed component name on its own line, sorted alphabetically

For example, if components "auth-service" and "api-gateway" failed, the report should look like:
```
FAILED_COMPONENTS_COUNT: 2

api-gateway
auth-service
```

Make sure the component names are extracted exactly as they appear in the log (the word immediately after `[FAILED]` and before the ` - ` separator).
