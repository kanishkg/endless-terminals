#!/bin/bash
# Auto-generated solve script
set -e

cat /home/user/pipelines/ios_builds.csv
cat /home/user/pipelines/android_builds.json
python3 << 'EOF'
import csv
import json

# Read iOS builds
ios_failed = []
with open('/home/user/pipelines/ios_builds.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['status'] == 'FAILED':
            ios_failed.append({
                'platform': 'ios',
                'build_id': row['build_id'],
                'app_name': row['app_name'],
                'duration_minutes': round(int(row['build_time_seconds']) / 60, 2),
                'branch': row['branch']
            })

# Read Android builds
with open('/home/user/pipelines/android_builds.json', 'r') as f:
    android_builds = json.load(f)

android_failed = []
for build in android_builds:
    if build['result'] == 'FAILED':
        android_failed.append({
            'platform': 'android',
            'build_id': build['buildId'],
            'app_name': build['appName'],
            'duration_minutes': round(build['buildDuration'] / 60, 2),
            'branch': build['branch']
        })

# Combine and sort
all_failed = ios_failed + android_failed
all_failed.sort(key=lambda x: (x['app_name'], x['build_id']))

# Write JSON report
with open('/home/user/pipelines/failed_builds_report.json', 'w') as f:
    json.dump(all_failed, f, indent=2)

# Write summary
with open('/home/user/pipelines/failure_summary.txt', 'w') as f:
    f.write(f"Total failed builds: {len(all_failed)}\n")
    f.write(f"iOS failures: {len(ios_failed)}\n")
    f.write(f"Android failures: {len(android_failed)}\n")

print("Done!")
EOF
cat /home/user/pipelines/failed_builds_report.json
cat /home/user/pipelines/failure_summary.txt
python3 -c "import json; json.load(open('/home/user/pipelines/failed_builds_report.json')); print('JSON is valid')"
