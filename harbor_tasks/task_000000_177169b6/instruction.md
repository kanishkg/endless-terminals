You are a penetration tester who has just completed a vulnerability scan using a custom scanning tool. The scan results have been saved to a log file at /home/user/pentest/scan_results.log. Your task is to filter this log file to extract only the critical and high severity vulnerabilities for your client report.

The log file contains entries in the following format:
```
[TIMESTAMP] [SEVERITY] [TARGET_IP] [VULN_ID] - Description
```

Where SEVERITY can be: CRITICAL, HIGH, MEDIUM, LOW, or INFO.

Please perform the following:

1. Extract all lines that contain either "CRITICAL" or "HIGH" severity vulnerabilities from the log file using regex-based filtering.

2. Save the filtered results to a new file at /home/user/pentest/critical_high_vulns.txt

3. Create a summary file at /home/user/pentest/vuln_summary.txt that contains exactly two lines:
   - First line: "CRITICAL: X" where X is the count of CRITICAL severity entries
   - Second line: "HIGH: Y" where Y is the count of HIGH severity entries

Make sure the filtered output file preserves the original log format and line ordering. The summary file should contain only the two count lines with no extra whitespace or blank lines.
