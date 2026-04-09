I need help setting up a git repository for tracking configuration files on my system. Here's what I need you to do:

1. Initialize a new git repository in the directory `/home/user/config-tracking`

2. Create a configuration file called `app.conf` inside that directory with the following exact content:
```
[database]
host=localhost
port=5432
name=production_db

[logging]
level=INFO
path=/var/log/app.log
```

3. Add this configuration file to git staging and make an initial commit with the exact commit message: `Initial configuration setup`

4. After completing these steps, create a log file at `/home/user/config-tracking/setup.log` that contains the following information in this exact format:
   - Line 1: The full path to the git repository
   - Line 2: The name of the tracked configuration file
   - Line 3: The commit hash (full 40-character SHA) of the initial commit
   - Line 4: The exact commit message used

Each piece of information should be on its own line with no extra whitespace or formatting. The log file should have exactly 4 lines.
