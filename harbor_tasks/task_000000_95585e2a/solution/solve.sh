#!/bin/bash
# Auto-generated solve script
set -e

cd /home/user/monitoring-project && git submodule add https://github.com/prometheus/alertmanager.git external/alertmanager
cd /home/user/monitoring-project && git submodule status external/alertmanager
cd /home/user/monitoring-project && git config --get submodule.external/alertmanager.url
cat > /home/user/monitoring-project/submodule-setup.log << 'EOF'
SUBMODULE_PATH: external/alertmanager
SUBMODULE_URL: https://github.com/prometheus/alertmanager.git
SUBMODULE_STATUS: bf98d8214337743a22f2eb7b35980f15ba745829 external/alertmanager (v0.32.0-2-gbf98d821)
SETUP_COMPLETE: true
EOF
cd /home/user/monitoring-project && cat submodule-setup.log && echo "---" && cat .gitmodules
