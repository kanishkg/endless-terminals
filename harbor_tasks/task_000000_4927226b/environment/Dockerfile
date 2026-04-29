FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/analyze && chmod 0777 /home/user && chmod 0777 /home/user/analyze

RUN python3.10 -m venv /home/user/analyze/venv

RUN /home/user/analyze/venv/bin/pip install mysql-connector-python==8.0.33

RUN /home/user/analyze/venv/bin/pip install mysql-connector==2.2.9

RUN touch /home/user/analyze/venv/lib/python3.10/site-packages/mysql/__init__.py

RUN cat > /home/user/analyze/slow_log.py << 'ENDSCRIPT'
#!/usr/bin/env python3
"""
Slow query log parser - groups queries by normalized fingerprint and outputs timing stats.
"""

import re
import sys
import mysql.connector

def upload_to_db(results):
    """Upload results to database (not used in main codepath)."""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="slow_query_stats"
    )
    cursor = conn.cursor()
    for fingerprint, total_time in results.items():
        cursor.execute(
            "INSERT INTO query_stats (fingerprint, total_time) VALUES (%s, %s)",
            (fingerprint, total_time)
        )
    conn.commit()
    cursor.close()
    conn.close()

def normalize_fingerprint(sql):
    """Normalize SQL by replacing literals with ? placeholders."""
    # Replace quoted strings
    normalized = re.sub(r"'[^']*'", "?", sql)
    # Replace numbers
    normalized = re.sub(r'\b\d+\.?\d*\b', '?', normalized)
    # Clean up whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def parse_slow_log(filepath):
    """Parse slow query log and return list of (query_time, sql) tuples."""
    queries = []
    # Bug 2: greedy regex that can grab extra content on some logs
    time_pattern = re.compile(r'#\s*Query_time:\s*(\d+\.\d+.*?)\s')

    with open(filepath, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        match = time_pattern.search(line)
        if match:
            try:
                query_time = float(match.group(1).split()[0])
            except ValueError:
                i += 1
                continue
            # Next non-comment line is the SQL
            i += 1
            while i < len(lines) and lines[i].startswith('#'):
                i += 1
            if i < len(lines):
                sql = lines[i].strip()
                if sql:
                    queries.append((query_time, sql))
        i += 1

    return queries

def group_by_fingerprint(queries):
    """Group queries by fingerprint and sum execution times."""
    groups = {}

    # Bug 1: Off-by-one with broken lookahead logic that double-counts
    for i in range(len(queries)):
        query_time, sql = queries[i]
        fingerprint = normalize_fingerprint(sql)

        if fingerprint not in groups:
            groups[fingerprint] = 0.0

        groups[fingerprint] += query_time

        # Broken "flush group" logic - re-adds current query time
        # when next query has different fingerprint
        if i + 1 < len(queries):
            next_sql = queries[i + 1][1]
            next_fingerprint = normalize_fingerprint(next_sql)
            if next_fingerprint != fingerprint:
                # Bug: accidentally adds query_time again
                groups[fingerprint] += query_time

    return groups

def main():
    if len(sys.argv) != 2:
        print("Usage: slow_log.py <logfile>")
        sys.exit(1)

    filepath = sys.argv[1]
    queries = parse_slow_log(filepath)
    groups = group_by_fingerprint(queries)

    print("Slow Query Analysis Results")
    print("=" * 60)
    for fingerprint, total_time in sorted(groups.items(), key=lambda x: -x[1]):
        print(f"Total: {total_time:.2f}s | {fingerprint}")
    print("=" * 60)

if __name__ == "__main__":
    main()
ENDSCRIPT

RUN chmod 0666 /home/user/analyze/slow_log.py

RUN cat > /home/user/analyze/test.log << 'ENDLOG'
# Time: 2024-01-15T10:00:01.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.823 Lock_time: 0.000 Rows_sent: 1 Rows_examined: 1000
SELECT * FROM orders WHERE customer_id = 12345;
# Time: 2024-01-15T10:00:02.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.412 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 50
UPDATE inventory SET qty = 100 WHERE sku = 'ABC123';
# Time: 2024-01-15T10:00:03.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.156 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (1, 'login', '2024-01-15');
# Time: 2024-01-15T10:00:04.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.891 Lock_time: 0.000 Rows_sent: 5 Rows_examined: 2000
SELECT * FROM orders WHERE customer_id = 67890;
# Time: 2024-01-15T10:00:05.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.378 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 45
UPDATE inventory SET qty = 250 WHERE sku = 'DEF456';
# Time: 2024-01-15T10:00:06.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.167 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (2, 'purchase', '2024-01-15');
# Time: 2024-01-15T10:00:07.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.756 Lock_time: 0.000 Rows_sent: 3 Rows_examined: 1500
SELECT * FROM orders WHERE customer_id = 11111;
# Time: 2024-01-15T10:00:08.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.445 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 60
UPDATE inventory SET qty = 75 WHERE sku = 'GHI789';
# Time: 2024-01-15T10:00:09.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.143 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (3, 'logout', '2024-01-15');
# Time: 2024-01-15T10:00:10.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.934 Lock_time: 0.000 Rows_sent: 2 Rows_examined: 1800
SELECT * FROM orders WHERE customer_id = 22222;
# Time: 2024-01-15T10:00:11.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.398 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 55
UPDATE inventory SET qty = 300 WHERE sku = 'JKL012';
# Time: 2024-01-15T10:00:12.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.178 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (4, 'view', '2024-01-15');
# Time: 2024-01-15T10:00:13.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.812 Lock_time: 0.000 Rows_sent: 4 Rows_examined: 1700
SELECT * FROM orders WHERE customer_id = 33333;
# Time: 2024-01-15T10:00:14.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.467 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 70
UPDATE inventory SET qty = 125 WHERE sku = 'MNO345';
# Time: 2024-01-15T10:00:15.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.134 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (5, 'search', '2024-01-15');
# Time: 2024-01-15T10:00:16.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.878 Lock_time: 0.000 Rows_sent: 6 Rows_examined: 2100
SELECT * FROM orders WHERE customer_id = 44444;
# Time: 2024-01-15T10:00:17.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.356 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 40
UPDATE inventory SET qty = 500 WHERE sku = 'PQR678';
# Time: 2024-01-15T10:00:18.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.189 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (6, 'cart_add', '2024-01-15');
# Time: 2024-01-15T10:00:19.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.923 Lock_time: 0.000 Rows_sent: 1 Rows_examined: 1900
SELECT * FROM orders WHERE customer_id = 55555;
# Time: 2024-01-15T10:00:20.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.423 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 65
UPDATE inventory SET qty = 80 WHERE sku = 'STU901';
# Time: 2024-01-15T10:00:21.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.145 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (7, 'checkout', '2024-01-15');
# Time: 2024-01-15T10:00:22.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.789 Lock_time: 0.000 Rows_sent: 2 Rows_examined: 1600
SELECT * FROM orders WHERE customer_id = 66666;
# Time: 2024-01-15T10:00:23.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.489 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 75
UPDATE inventory SET qty = 200 WHERE sku = 'VWX234';
# Time: 2024-01-15T10:00:24.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.123 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (8, 'payment', '2024-01-15');
# Time: 2024-01-15T10:00:25.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.867 Lock_time: 0.000 Rows_sent: 3 Rows_examined: 1850
SELECT * FROM orders WHERE customer_id = 77777;
# Time: 2024-01-15T10:00:26.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.334 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 35
UPDATE inventory SET qty = 150 WHERE sku = 'YZA567';
# Time: 2024-01-15T10:00:27.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.198 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (9, 'confirm', '2024-01-15');
# Time: 2024-01-15T10:00:28.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.945 Lock_time: 0.000 Rows_sent: 5 Rows_examined: 2200
SELECT * FROM orders WHERE customer_id = 88888;
# Time: 2024-01-15T10:00:29.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.401 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 50
UPDATE inventory SET qty = 350 WHERE sku = 'BCD890';
# Time: 2024-01-15T10:00:30.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.167 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (10, 'ship', '2024-01-15');
# Time: 2024-01-15T10:00:31.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.801 Lock_time: 0.000 Rows_sent: 1 Rows_examined: 1400
SELECT * FROM orders WHERE customer_id = 99999;
# Time: 2024-01-15T10:00:32.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.456 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 80
UPDATE inventory SET qty = 90 WHERE sku = 'EFG123';
# Time: 2024-01-15T10:00:33.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.112 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (11, 'deliver', '2024-01-15');
# Time: 2024-01-15T10:00:34.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.856 Lock_time: 0.000 Rows_sent: 4 Rows_examined: 1950
SELECT * FROM orders WHERE customer_id = 10101;
# Time: 2024-01-15T10:00:35.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.378 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 42
UPDATE inventory SET qty = 275 WHERE sku = 'HIJ456';
# Time: 2024-01-15T10:00:36.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.156 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (12, 'return', '2024-01-15');
# Time: 2024-01-15T10:00:37.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.912 Lock_time: 0.000 Rows_sent: 2 Rows_examined: 2050
SELECT * FROM orders WHERE customer_id = 20202;
# Time: 2024-01-15T10:00:38.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.512 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 85
UPDATE inventory SET qty = 60 WHERE sku = 'KLM789';
# Time: 2024-01-15T10:00:39.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.134 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (13, 'refund', '2024-01-15');
# Time: 2024-01-15T10:00:40.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.778 Lock_time: 0.000 Rows_sent: 3 Rows_examined: 1650
SELECT * FROM orders WHERE customer_id = 30303;
# Time: 2024-01-15T10:00:41.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.389 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 48
UPDATE inventory SET qty = 400 WHERE sku = 'NOP012';
# Time: 2024-01-15T10:00:42.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.189 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (14, 'review', '2024-01-15');
# Time: 2024-01-15T10:00:43.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.834 Lock_time: 0.000 Rows_sent: 1 Rows_examined: 1750
SELECT * FROM orders WHERE customer_id = 40404;
# Time: 2024-01-15T10:00:44.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.445 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 58
UPDATE inventory SET qty = 175 WHERE sku = 'QRS345';
# Time: 2024-01-15T10:00:45.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.145 Lock_time: 0.000 Rows_sent: 0 Rows_examined: 0
INSERT INTO audit_log VALUES (15, 'wishlist', '2024-01-15');
# Time: 2024-01-15T10:00:46.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.638 Lock_time: 0.000 Rows_sent: 2 Rows_examined: 1300
SELECT * FROM orders WHERE customer_id = 50505;
# Time: 2024-01-15T10:00:47.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.401 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 52
UPDATE inventory SET qty = 225 WHERE sku = 'TUV678';
# Time: 2024-01-15T10:00:48.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.401 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 62
UPDATE inventory SET qty = 110 WHERE sku = 'WXY901';
# Time: 2024-01-15T10:00:49.000000Z
# User@Host: app[app] @ localhost []
# Query_time: 0.423 Lock_time: 0.001 Rows_sent: 0 Rows_examined: 68
UPDATE inventory SET qty = 320 WHERE sku = 'ZAB234';
ENDLOG

RUN chmod 0444 /home/user/analyze/test.log

RUN chown -R root:root /home/user/analyze && \
    chmod 0777 /home/user/analyze && \
    chmod 0666 /home/user/analyze/slow_log.py && \
    chmod 0444 /home/user/analyze/test.log && \
    chmod -R 0755 /home/user/analyze/venv && \
    find /home/user/analyze/venv -type f -exec chmod 0644 {} \; && \
    chmod 0755 /home/user/analyze/venv/bin/* && \
    find /home/user/analyze/venv -type d -exec chmod 0755 {} \;

WORKDIR /home/user

CMD ["/bin/bash"]
