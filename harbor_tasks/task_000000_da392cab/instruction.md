You are a log analyst investigating access patterns on a web server. There is a directory at /home/user/server_logs containing several Apache-style access log files from different dates.

Your task is to find all log entries across all .log files in the /home/user/server_logs directory that contain HTTP 404 error responses and save them to a single consolidated file.

Specifically:
1. Search through all files ending in .log within /home/user/server_logs
2. Find all lines that contain the pattern " 404 " (the HTTP status code 404 surrounded by spaces)
3. Save all matching lines to a new file at /home/user/analysis/404_errors.txt

The output file should contain the raw matching lines exactly as they appear in the original log files, with each match on its own line. The file should be created even if no matches are found (in which case it would be empty).

Make sure the /home/user/analysis directory exists before writing the output file.
