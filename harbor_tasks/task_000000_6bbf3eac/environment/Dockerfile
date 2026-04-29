FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pyyaml pandas

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/etl/data \
    && mkdir -p /home/user/etl/scripts \
    && mkdir -p /home/user/etl/clean \
    && mkdir -p /home/user/etl/config

RUN python3 << 'PYSCRIPT'
import csv
import random
import os

random.seed(42)

products = ['Widget', 'Gadget', 'Gizmo', 'Doohickey', 'Thingamajig', 'Whatsit', 'Doodad', 'Contraption']
regions = ['North', 'South', 'East', 'West', 'Central']

# Generate sales_2023.csv
with open('/home/user/etl/data/sales_2023.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'product', 'region', 'quantity', 'price', 'date'])
    for i in range(500):
        writer.writerow([
            i + 1,
            random.choice(products),
            random.choice(regions),
            random.randint(1, 100),
            round(random.uniform(10.0, 500.0), 2),
            f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        ])

# Generate sales_2024.csv
with open('/home/user/etl/data/sales_2024.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'product', 'region', 'quantity', 'price', 'date'])
    for i in range(500):
        writer.writerow([
            i + 1,
            random.choice(products),
            random.choice(regions),
            random.randint(1, 100),
            round(random.uniform(10.0, 500.0), 2),
            f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        ])

# Generate inventory.csv
with open('/home/user/etl/data/inventory.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'product', 'warehouse', 'stock', 'reorder_level', 'last_updated'])
    warehouses = ['WH-A', 'WH-B', 'WH-C', 'WH-D']
    for i in range(500):
        writer.writerow([
            i + 1,
            random.choice(products),
            random.choice(warehouses),
            random.randint(0, 1000),
            random.randint(10, 100),
            f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        ])
PYSCRIPT

RUN cat << 'CLEANPY' > /home/user/etl/scripts/clean.py
#!/usr/bin/env python3
"""
Clean a CSV file: remove rows with missing values, strip whitespace from strings,
ensure numeric columns are valid.
"""
import sys
import csv
import os

def clean_csv(input_file, output_file):
    with open(input_file, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        rows = []
        for row in reader:
            # Skip rows with empty values
            if any(v.strip() == '' for v in row.values()):
                continue
            # Strip whitespace from all values
            cleaned_row = {k: v.strip() for k, v in row.items()}
            rows.append(cleaned_row)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Cleaned {input_file} -> {output_file} ({len(rows)} rows)")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <output.csv>", file=sys.stderr)
        sys.exit(1)
    clean_csv(sys.argv[1], sys.argv[2])
CLEANPY

RUN cat << 'JOINPY' > /home/user/etl/scripts/join.py
#!/usr/bin/env python3
"""
Join multiple cleaned CSV files into a single joined.csv.
Reads file list from clean/manifest.txt
"""
import sys
import csv
import os
import time

def join_csvs(manifest_file, output_file):
    # Read manifest to get list of files
    if not os.path.exists(manifest_file):
        print(f"Error: Manifest file {manifest_file} not found", file=sys.stderr)
        sys.exit(1)

    with open(manifest_file, 'r') as f:
        files = [line.strip() for line in f if line.strip()]

    if not files:
        print("Error: No files listed in manifest", file=sys.stderr)
        sys.exit(1)

    all_rows = []
    all_fieldnames = set()

    for filepath in files:
        if not os.path.exists(filepath):
            print(f"Error: File {filepath} not found", file=sys.stderr)
            sys.exit(1)

        with open(filepath, 'r', newline='') as f:
            reader = csv.DictReader(f)
            all_fieldnames.update(reader.fieldnames)
            for row in reader:
                row['_source_file'] = os.path.basename(filepath)
                all_rows.append(row)

    # Sort fieldnames for consistent output
    fieldnames = sorted(list(all_fieldnames)) + ['_source_file']

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Joined {len(files)} files -> {output_file} ({len(all_rows)} rows)")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <manifest.txt> <output.csv>", file=sys.stderr)
        sys.exit(1)
    join_csvs(sys.argv[1], sys.argv[2])
JOINPY

RUN cat << 'SUMPY' > /home/user/etl/scripts/summarize.py
#!/usr/bin/env python3
"""
Generate summary statistics from joined.csv.
Also reads config/params.yaml for aggregation settings.
"""
import sys
import csv
import os
import yaml

def summarize(input_file, output_file, config_file='config/params.yaml'):
    # Read config (hidden dependency!)
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f) or {}

    include_source_breakdown = config.get('include_source_breakdown', True)

    with open(input_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Generate summary
    summary_rows = []

    # Total row count
    summary_rows.append({'metric': 'total_rows', 'value': len(rows)})

    # Count by source file
    if include_source_breakdown:
        source_counts = {}
        for row in rows:
            src = row.get('_source_file', 'unknown')
            source_counts[src] = source_counts.get(src, 0) + 1

        for src, count in sorted(source_counts.items()):
            summary_rows.append({'metric': f'rows_from_{src}', 'value': count})

    # Numeric summaries if quantity/price columns exist
    if rows and 'quantity' in rows[0]:
        total_qty = sum(int(r.get('quantity', 0)) for r in rows if r.get('quantity', '').isdigit())
        summary_rows.append({'metric': 'total_quantity', 'value': total_qty})

    if rows and 'price' in rows[0]:
        try:
            total_price = sum(float(r.get('price', 0)) for r in rows if r.get('price'))
            summary_rows.append({'metric': 'total_price', 'value': round(total_price, 2)})
        except ValueError:
            pass

    if rows and 'stock' in rows[0]:
        try:
            total_stock = sum(int(r.get('stock', 0)) for r in rows if r.get('stock', '').isdigit())
            summary_rows.append({'metric': 'total_stock', 'value': total_stock})
        except ValueError:
            pass

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['metric', 'value'])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Summarized {input_file} -> {output_file} ({len(summary_rows)} metrics)")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <output.csv>", file=sys.stderr)
        sys.exit(1)

    # Look for config relative to script location or current dir
    config_paths = [
        'config/params.yaml',
        os.path.join(os.path.dirname(sys.argv[1]), '..', 'config', 'params.yaml'),
    ]
    config_file = None
    for cp in config_paths:
        if os.path.exists(cp):
            config_file = cp
            break

    summarize(sys.argv[1], sys.argv[2], config_file or 'config/params.yaml')
SUMPY

RUN cat << 'CONFIGYAML' > /home/user/etl/config/params.yaml
# Configuration for summarize.py
include_source_breakdown: true
decimal_places: 2
CONFIGYAML

RUN cat << 'MAKEFILE' > /home/user/etl/Makefile
# ETL Pipeline Makefile
# Cleans CSVs, joins them, and generates summary

SHELL := /bin/bash

# Source files
SOURCES := $(wildcard data/*.csv)
# Derive clean targets from sources
CLEAN_TARGETS := $(patsubst data/%.csv,clean/%.csv,$(SOURCES))

.PHONY: all clean

all: summary.csv

# Pattern rule for cleaning - uses $$@ for secondary expansion but directive is MISSING
# BUG #1: $$@ without .SECONDEXPANSION means it's interpreted as literal $@ in first pass
clean/%.csv: data/%.csv
	@mkdir -p clean
	python3 scripts/clean.py $< $$@

# Generate manifest of cleaned files
clean/manifest.txt:
	@mkdir -p clean
	@ls clean/*.csv 2>/dev/null > clean/manifest.txt || touch clean/manifest.txt

# BUG #2: $(wildcard clean/*.csv) is evaluated at Makefile parse time
# On first run when clean/ is empty, this evaluates to nothing
# So joined.csv has NO dependencies after first run
# BUG #3: Missing dependency on clean/manifest.txt - race condition with -j4
joined.csv: $(wildcard clean/*.csv)
	python3 scripts/join.py clean/manifest.txt joined.csv

# BUG #4: Missing dependency on config/params.yaml
# summarize.py secretly reads this file but it's not listed here
summary.csv: joined.csv
	python3 scripts/summarize.py joined.csv summary.csv

clean:
	rm -rf clean/*.csv clean/manifest.txt joined.csv summary.csv
MAKEFILE

RUN cd /home/user/etl && \
    mkdir -p clean && \
    python3 scripts/clean.py data/sales_2023.csv clean/sales_2023.csv && \
    python3 scripts/clean.py data/sales_2024.csv clean/sales_2024.csv && \
    python3 scripts/clean.py data/inventory.csv clean/inventory.csv && \
    ls clean/*.csv > clean/manifest.txt && \
    python3 scripts/join.py clean/manifest.txt joined.csv && \
    python3 scripts/summarize.py joined.csv summary.csv

RUN chmod -R 0777 /home/user/etl

CMD ["/bin/bash"]
