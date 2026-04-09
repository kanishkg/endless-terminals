I have an incident log file at /home/user/incidents/incident_log.csv that contains our recent production incidents. The CSV has the following columns: incident_id, timestamp, severity, service, status, assigned_to.

I need you to help me with some quick triage work:

1. First, filter out only the incidents that have severity "critical" or "high" and are still in "open" status.

2. Convert the filtered results to JSON format and save it to /home/user/incidents/priority_incidents.json. The JSON should be an array of objects, where each object represents one incident with all the original fields as keys.

3. Create a summary file at /home/user/incidents/triage_summary.txt that contains:
   - Line 1: "Priority Incidents Report"
   - Line 2: "Total critical/high open incidents: X" (where X is the count of filtered incidents)
   - Line 3: A blank line
   - Lines 4+: List each affected service name (from the filtered incidents), one per line, sorted alphabetically, with no duplicates

The JSON file should be valid JSON with proper formatting (can be compact or pretty-printed, but must be valid). Each incident object should have string values for all fields exactly as they appear in the CSV.
