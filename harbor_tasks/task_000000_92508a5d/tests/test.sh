#!/bin/bash

apt-get update
apt-get install -y curl
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
source $HOME/.local/bin/env
# Run pytest tests
cd /home/user
uvx \
  --python 3.12 \
  --with pytest==8.4.1 \
  pytest /tests/test_final_state.py -v
# Check exit code and write reward
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
