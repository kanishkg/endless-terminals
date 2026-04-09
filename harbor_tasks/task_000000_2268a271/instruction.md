You are a deployment engineer preparing an application update package for distribution. You need to create a compressed archive of the application files for deployment to production servers.

There is a directory at /home/user/app_release_v2.3.1 containing the following application files that need to be packaged:
- main.py (the main application script)
- config.json (configuration file)
- requirements.txt (Python dependencies)
- README.md (documentation)
- lib/ (a subdirectory containing helper modules)
  - utils.py
  - database.py

Your task is to create a gzip-compressed tar archive of this entire directory. The archive must be named "app_release_v2.3.1.tar.gz" and must be placed in the /home/user/deployments directory.

After creating the archive, verify the archive was created successfully by listing its contents and save the output to a log file named "archive_contents.log" in the /home/user/deployments directory. The log file should contain the verbose listing of all files and directories within the archive (showing file permissions, ownership, size, date, and full paths).

Requirements:
1. The archive must preserve the directory structure with "app_release_v2.3.1" as the root directory inside the archive
2. The archive file must be located at /home/user/deployments/app_release_v2.3.1.tar.gz
3. The verification log must be located at /home/user/deployments/archive_contents.log
4. The log file must contain entries for all 7 items: the main directory, the lib subdirectory, and all 6 files (main.py, config.json, requirements.txt, README.md, lib/utils.py, lib/database.py)
