I'm a mobile build engineer and I need help analyzing our iOS and Android build pipeline data. I have two data files that need to be processed and combined.

First, there's a CSV file at `/home/user/pipelines/ios_builds.csv` containing iOS build information with columns: build_id, app_name, build_time_seconds, status, branch, timestamp.

Second, there's a JSON file at `/home/user/pipelines/android_builds.json` containing Android build records with fields: buildId, appName, buildDuration, result, branch, date.

I need you to do the following:

1. Extract all FAILED builds from both files (status="FAILED" for iOS, result="FAILED" for Android).

2. Create a unified JSON report at `/home/user/pipelines/failed_builds_report.json` that combines the failed builds from both platforms. The output JSON should be an array of objects with this exact structure for each failed build:
   - "platform": either "ios" or "android"
   - "build_id": the build identifier (as a string)
   - "app_name": the application name
   - "duration_minutes": the build time converted to minutes (rounded to 2 decimal places)
   - "branch": the branch name

   The array should be sorted alphabetically by app_name, and if app_names are the same, then by build_id ascending.

3. Create a summary file at `/home/user/pipelines/failure_summary.txt` with exactly these three lines:
   - Line 1: `Total failed builds: X` (where X is the total count of failed builds from both platforms)
   - Line 2: `iOS failures: Y` (where Y is the count of failed iOS builds)
   - Line 3: `Android failures: Z` (where Z is the count of failed Android builds)

Make sure the JSON file is valid and properly formatted with 2-space indentation.
