#!/bin/bash
# Auto-generated solve script
set -e

ls -la /home/user/app_release_v2.3.1
ls -la /home/user/app_release_v2.3.1/lib
mkdir -p /home/user/deployments
tar -czvf /home/user/deployments/app_release_v2.3.1.tar.gz -C /home/user app_release_v2.3.1
tar -tzvf /home/user/deployments/app_release_v2.3.1.tar.gz > /home/user/deployments/archive_contents.log
cat /home/user/deployments/archive_contents.log
ls -la /home/user/deployments/
