FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the incidents directory
RUN mkdir -p /home/user/incidents && chmod 0777 /home/user/incidents

# Create the incident_log.csv file with the required content
RUN cat <<EOF > /home/user/incidents/incident_log.csv
incident_id,timestamp,severity,service,status,assigned_to
INC001,2024-01-15T08:30:00Z,critical,payment-api,open,alice
INC002,2024-01-15T09:15:00Z,low,user-service,closed,bob
INC003,2024-01-15T10:00:00Z,high,payment-api,open,charlie
INC004,2024-01-15T10:45:00Z,medium,notification-service,open,alice
INC005,2024-01-15T11:30:00Z,critical,database-cluster,open,dave
INC006,2024-01-15T12:00:00Z,high,auth-service,closed,eve
INC007,2024-01-15T12:45:00Z,high,inventory-service,open,frank
INC008,2024-01-15T13:30:00Z,critical,payment-api,closed,alice
EOF

# Set permissions on the CSV file
RUN chmod 0666 /home/user/incidents/incident_log.csv

# Set working directory
WORKDIR /home/user
