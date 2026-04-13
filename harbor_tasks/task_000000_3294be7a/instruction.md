I need help analyzing and transforming some server access logs. I have a raw Apache-style access log file at `/home/user/logs/access.log` that contains web server traffic data from the past week.

Here's what I need you to do:

1. First, extract all unique IP addresses from the log file and count how many requests each IP made. Save this to `/home/user/reports/ip_counts.txt` with the format `COUNT IP_ADDRESS` (count first, then IP, separated by a single space), sorted numerically in descending order by count.

2. Next, identify all requests that resulted in HTTP 4xx or 5xx error codes. Extract just the IP address, HTTP status code, and the requested URL path for these error requests. Save this to `/home/user/reports/errors.csv` as a proper CSV file with a header row `ip,status,path` and each field properly formatted (no extra spaces around fields).

3. Calculate the total bandwidth transferred by summing the bytes field (the last numeric field before the user agent string in each log entry). Save just the total number (in bytes, as an integer with no commas or formatting) to `/home/user/reports/total_bandwidth.txt`.

4. Find the top 5 most frequently requested URL paths (excluding query strings - just the path portion). Save these to `/home/user/reports/top_paths.txt` with format `COUNT PATH` (count first, then path, separated by a single space), one per line, sorted by count in descending order.

5. Finally, create a summary file at `/home/user/reports/summary.txt` containing exactly these four lines:
   - Line 1: `Unique IPs: N` (where N is the count of unique IP addresses)
   - Line 2: `Total Requests: N` (where N is total number of log entries)
   - Line 3: `Error Requests: N` (where N is count of 4xx/5xx responses)
   - Line 4: `Total Bandwidth: N bytes` (where N is the total bandwidth)

Make sure the `/home/user/reports/` directory exists before creating the output files.
