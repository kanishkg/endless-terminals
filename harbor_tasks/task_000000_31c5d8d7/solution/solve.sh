#!/bin/bash
# Auto-generated solve script
set -e

cat /home/user/incidents/incident_log.csv
python3 << 'EOF'
import csv
import json

# Read and filter the CSV
filtered = []
with open('/home/user/incidents/incident_log.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['severity'] in ('critical', 'high') and row['status'] == 'open':
            filtered.append(row)

# Write JSON file
with open('/home/user/incidents/priority_incidents.json', 'w') as f:
    json.dump(filtered, f, indent=2)

# Get unique services sorted
services = sorted(set(row['service'] for row in filtered))

# Write summary file
with open('/home/user/incidents/triage_summary.txt', 'w') as f:
    f.write("Priority Incidents Report\n")
    f.write(f"Total critical/high open incidents: {len(filtered)}\n")
    f.write("\n")
    for service in services:
        f.write(f"{service}\n")

print("Done!")
EOF
cat /home/user/incidents/priority_incidents.json
cat /home/user/incidents/triage_summary.txt
python3 -m json.tool /home/user/incidents/priority_incidents.json > /dev/null && echo "Valid JSON"
