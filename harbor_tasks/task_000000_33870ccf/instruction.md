You are an operations engineer responding to a disk space alert on a production server. The monitoring system has flagged that disk usage is high, and you need to quickly identify the problem areas and create a comprehensive incident report.

Your task is to perform a thorough disk usage analysis and generate a structured incident report at `/home/user/incident_report.txt`.

**Step 1: Identify Large Directories**
Analyze the `/home/user/app_data` directory structure to find the top 5 largest subdirectories. You need to capture their sizes in human-readable format.

**Step 2: Find Large Files**
Search the entire `/home/user/app_data` directory tree for files larger than 50MB. Record the full path and size of each file found.

**Step 3: Identify Old Log Files**
Find all files with the `.log` extension under `/home/user/app_data` that were modified more than 7 days ago. These are candidates for cleanup.

**Step 4: Analyze File Type Distribution**
Count the total number of files for each file extension in `/home/user/app_data` to understand what types of files are consuming space.

**Step 5: Generate the Incident Report**
Create the file `/home/user/incident_report.txt` with the following exact structure:

```
=== DISK USAGE INCIDENT REPORT ===
Generated: [YYYY-MM-DD HH:MM:SS]

--- TOP 5 LARGEST DIRECTORIES ---
[List each directory on its own line with format: SIZE PATH]

--- FILES LARGER THAN 50MB ---
[List each file on its own line with format: SIZE PATH]
[If no files found, write: No files larger than 50MB found]

--- OLD LOG FILES (>7 days) ---
[List each log file path on its own line]
[If no old logs found, write: No old log files found]

--- FILE TYPE DISTRIBUTION ---
[List each extension with count in format: COUNT .EXTENSION]
[Sort by count in descending order]

--- SUMMARY ---
Total directories analyzed: [number]
Large files found: [number]
Old log files found: [number]
=== END REPORT ===
```

The timestamp in the report should reflect when you generated it. All paths should be absolute paths. The SIZE values should be in human-readable format (K, M, G). Ensure the report sections are separated by blank lines as shown above.

Run the analysis tasks efficiently - where possible, execute independent analyses in parallel to minimize incident response time.
