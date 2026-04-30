FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/etl/input \
    && mkdir -p /home/user/etl/output \
    && mkdir -p /home/user/etl/lib \
    && mkdir -p /home/user/etl/logs

RUN cat <<'EOF' > /home/user/etl/lib/parsers.py
"""
Helper functions for parsing transaction data.
"""
import re


def parse_amount(s):
    """
    Parse an amount string like "$1,234.56" and return a float.
    Strips currency symbols and thousand separators.
    """
    # Remove dollar sign and commas
    cleaned = re.sub(r'[\$,]', '', s)
    return float(cleaned)
EOF

RUN cat <<'EOF' > /home/user/etl/lib/__init__.py
# ETL library package
EOF

RUN cat <<'EOF' > /home/user/etl/transform.py
#!/usr/bin/env python3
"""
ETL script to transform transactions from JSON to CSV format.
"""
import json
import csv
import os
import sys
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from parsers import parse_amount


def get_log_path():
    return os.path.join(os.path.dirname(__file__), 'logs', 'transform.log')


def get_input_path():
    return os.path.join(os.path.dirname(__file__), 'input', 'transactions.json')


def get_output_path():
    return os.path.join(os.path.dirname(__file__), 'output', 'transactions.csv')


def log_warning(message):
    """Append warning message to log file."""
    log_path = get_log_path()
    timestamp = datetime.now().isoformat()
    with open(log_path, 'a') as f:
        f.write(f"{timestamp} WARN: {message}\n")


def transform():
    """Main transformation function."""
    input_path = get_input_path()
    output_path = get_output_path()

    # Load input JSON
    with open(input_path, 'r') as f:
        transactions = json.load(f)

    # Write CSV output
    fieldnames = ['id', 'date', 'amount', 'currency', 'department', 'description']

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for txn in transactions:
            try:
                # Parse the amount to numeric value
                amount = parse_amount(txn['amount'])

                row = {
                    'id': txn['id'],
                    'date': txn['date'],
                    'amount': amount,
                    'currency': txn['currency'],
                    'department': txn['department'],
                    'description': txn['description']
                }
                writer.writerow(row)
            except Exception as e:
                log_warning(f"skipping row {txn.get('id', 'unknown')}: {e}")
                continue

    print(f"Transformation complete. Output written to {output_path}")


if __name__ == '__main__':
    transform()
EOF

RUN python3 <<'PYSCRIPT'
import json
import random
import string
from datetime import datetime, timedelta

random.seed(42)

departments = ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations', 'Legal', 'Support']
descriptions_usd = [
    'Office supplies purchase',
    'Software license renewal',
    'Client dinner expense',
    'Travel reimbursement',
    'Conference registration',
    'Equipment purchase',
    'Consulting fee',
    'Marketing campaign',
    'Training materials',
    'Subscription service'
]
descriptions_eur = [
    'EU vendor payment',
    'International shipping',
    'European conference',
    'GDPR compliance audit',
    'EU marketing spend',
    'Cross-border transfer',
    'European supplier',
    'VAT payment',
    'EU office supplies',
    'International consulting'
]

transactions = []
base_date = datetime(2024, 1, 1)

# Generate 206 USD transactions
for i in range(206):
    txn_id = 'TXN-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    date = base_date + timedelta(days=random.randint(0, 180))
    amount_val = round(random.uniform(50, 15000), 2)
    amount_str = '${:,.2f}'.format(amount_val)

    transactions.append({
        'id': txn_id,
        'date': date.strftime('%Y-%m-%dT%H:%M:%S'),
        'amount': amount_str,
        'currency': 'USD',
        'department': random.choice(departments),
        'description': random.choice(descriptions_usd)
    })

# Generate 41 EUR transactions
for i in range(41):
    txn_id = 'TXN-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    date = base_date + timedelta(days=random.randint(0, 180))
    amount_val = round(random.uniform(100, 12000), 2)
    amount_str = '€{:,.2f}'.format(amount_val)

    transactions.append({
        'id': txn_id,
        'date': date.strftime('%Y-%m-%dT%H:%M:%S'),
        'amount': amount_str,
        'currency': 'EUR',
        'department': random.choice(departments),
        'description': random.choice(descriptions_eur)
    })

# Shuffle to mix USD and EUR
random.shuffle(transactions)

with open('/home/user/etl/input/transactions.json', 'w') as f:
    json.dump(transactions, f, indent=2)

print(f"Generated {len(transactions)} transactions")
PYSCRIPT

WORKDIR /home/user/etl

RUN git init && \
    git config user.email "dev@company.com" && \
    git config user.name "Developer"

RUN git add lib/__init__.py && \
    git commit -m "Initial commit: project structure"

RUN git add lib/parsers.py && \
    git commit -m "Add parsers module with amount parsing"

RUN git add transform.py && \
    git commit -m "Add main transform script"

RUN git add input/transactions.json && \
    git commit -m "Add EUR currency support to input data"

RUN : > /home/user/etl/logs/transform.log

RUN python3 /home/user/etl/transform.py

RUN chmod -R 0777 /home/user/etl

WORKDIR /home/user

CMD ["/bin/bash"]
