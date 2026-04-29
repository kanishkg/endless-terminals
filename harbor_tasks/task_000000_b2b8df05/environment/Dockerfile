FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/data && chmod 0777 /home/user && chmod 0777 /home/user/data

RUN cat > /tmp/setup_db.py << 'ENDPYTHON'
import sqlite3
import random
import string
from datetime import datetime, timedelta

random.seed(42)

conn = sqlite3.connect('/home/user/data/survey.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE responses (
        id INTEGER PRIMARY KEY,
        email TEXT,
        response TEXT,
        submitted_at TEXT
    )
''')

def random_email():
    name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
    domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com', 'test.org'])
    return f"{name}@{domain}"

def random_response():
    responses = [
        "Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied",
        "Great service!", "Could be better", "No comment", "Excellent experience",
        "Will recommend to others", "Needs improvement", "Average", "Outstanding"
    ]
    return random.choice(responses)

def random_timestamp(base_date, offset_days=0):
    dt = base_date + timedelta(
        days=offset_days + random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return dt.strftime('%Y-%m-%d %H:%M:%S')

base_date = datetime(2024, 1, 1)

emails_298 = [random_email() for _ in range(298)]
emails_298 = list(set(emails_298))
while len(emails_298) < 298:
    emails_298.append(random_email())
    emails_298 = list(set(emails_298))
emails_298 = emails_298[:298]

rows = []
row_id = 1

for email in emails_298:
    num_submissions = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
    for _ in range(num_submissions):
        ts = random_timestamp(base_date, random.randint(0, 60))
        resp = random_response()
        rows.append((row_id, email, resp, ts))
        row_id += 1

for _ in range(14):
    ts = random_timestamp(base_date, random.randint(0, 60))
    resp = random_response()
    rows.append((row_id, None, resp, ts))
    row_id += 1

while len(rows) < 847:
    email = random.choice(emails_298)
    ts = random_timestamp(base_date, random.randint(0, 60))
    resp = random_response()
    rows.append((row_id, email, resp, ts))
    row_id += 1

rows = rows[:847]

for i, row in enumerate(rows):
    rows[i] = (i + 1, row[1], row[2], row[3])

cursor.executemany(
    'INSERT INTO responses (id, email, response, submitted_at) VALUES (?, ?, ?, ?)',
    rows
)

conn.commit()

cursor.execute('SELECT COUNT(*) FROM responses')
total = cursor.fetchone()[0]
print(f"Total rows: {total}")

cursor.execute('SELECT COUNT(DISTINCT email) FROM responses WHERE email IS NOT NULL')
distinct_non_null = cursor.fetchone()[0]
print(f"Distinct non-NULL emails: {distinct_non_null}")

cursor.execute('SELECT COUNT(*) FROM responses WHERE email IS NULL')
null_count = cursor.fetchone()[0]
print(f"NULL email rows: {null_count}")

conn.close()
ENDPYTHON

RUN python3 /tmp/setup_db.py && rm /tmp/setup_db.py

RUN cat > /home/user/data/clean.sql << 'ENDSQL'
DROP TABLE IF EXISTS responses_clean;
CREATE TABLE responses_clean AS
SELECT r.*
FROM responses r
INNER JOIN (
    SELECT email, MIN(submitted_at) as first_sub
    FROM responses
    GROUP BY email
) earliest ON r.email = earliest.email AND r.submitted_at = earliest.first_sub;
ENDSQL

RUN chmod 0666 /home/user/data/survey.db && chmod 0666 /home/user/data/clean.sql

WORKDIR /home/user

CMD ["/bin/bash"]
