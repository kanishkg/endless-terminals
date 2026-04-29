FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/reports/data && chmod -R 0777 /home/user

RUN cat > /home/user/reports/data/sales.csv << 'EOF'
product,quantity,price
Widget A,100,25.50
Widget B,50,30.00
Widget C,75,15.75
EOF

RUN cat > /home/user/reports/data/inventory.csv << 'EOF'
item,stock,reorder_level
Widget A,500,100
Widget B,200,50
Widget C,350,75
EOF

RUN cat > /home/user/reports/generate.py << 'EOF'
#!/usr/bin/env python3
import csv
import os

def main():
    print "Summary Report"
    print "=============="

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    total = 0

    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                total += len(rows)

    print "Processed files from data directory"
    print "Total:", total, "records"

if __name__ == '__main__':
    main()
EOF

RUN chmod 0777 /home/user/reports/generate.py && \
    chmod 0777 /home/user/reports/data/sales.csv && \
    chmod 0777 /home/user/reports/data/inventory.csv && \
    chmod 0777 /home/user/reports/data && \
    chmod 0777 /home/user/reports
