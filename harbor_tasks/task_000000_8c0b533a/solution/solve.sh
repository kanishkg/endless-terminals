#!/bin/bash
# Auto-generated solve script
set -e

cat /home/user/data/users.json
mkdir -p /home/user/output
jq -r '["id","name","email","signup_date"], (.[] | [.id, .name, .email, .signup_date]) | @csv' /home/user/data/users.json | sed 's/"//g' > /home/user/output/users.csv
python3 -c "
import json
import csv

with open('/home/user/data/users.json', 'r') as f:
    users = json.load(f)

with open('/home/user/output/users.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'email', 'signup_date'])
    for user in users:
        writer.writerow([user['id'], user['name'], user['email'], user['signup_date']])
"
cat /home/user/output/users.csv
