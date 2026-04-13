#!/bin/bash
# Auto-generated solve script
set -e

mkdir -p /home/user/sales_analysis && cd /home/user/sales_analysis && git init
cd /home/user/sales_analysis && git submodule add /home/user/shared_utils utils
git config --global protocol.file.allow always
cd /home/user/sales_analysis && git submodule add /home/user/shared_utils utils
cd /home/user/sales_analysis && git commit -m "Add shared utilities submodule"
git config --global user.email "analyst@example.com" && git config --global user.name "Data Analyst"
cd /home/user/sales_analysis && git commit -m "Add shared utilities submodule"
cd /home/user/sales_analysis && git submodule status
cd /home/user/sales_analysis && cat .gitmodules
cd /home/user/sales_analysis && git submodule status > setup_log.txt && echo "SUBMODULE_PATH: $(git config -f .gitmodules --get submodule.utils.path)" >> setup_log.txt && echo "SUBMODULE_URL: $(git config -f .gitmodules --get submodule.utils.url)" >> setup_log.txt
cat /home/user/sales_analysis/setup_log.txt
cd /home/user/sales_analysis && git log --oneline && ls -la
