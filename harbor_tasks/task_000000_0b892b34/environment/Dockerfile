FROM ubuntu:22.04

# Install Python 3, pip, and required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest and scipy via pip
RUN pip3 install pytest scipy

# Create /home/user directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the audit directory
RUN mkdir -p /home/user/audit && chmod 0777 /home/user/audit

# Create the constraints.csv file
RUN cat <<EOF > /home/user/audit/constraints.csv
constraint_name,type,coefficients,rhs
min_morning_coverage,GE,1|1|0|0|0|0,15
min_afternoon_coverage,GE,0|0|1|1|0|0,12
min_evening_coverage,GE,0|0|0|0|1|1,8
max_total_staff,LE,1|1|1|1|1|1,50
budget_limit,LE,25|30|22|35|28|32,1200
senior_ratio,GE,-0.3|0.7|-0.3|0.7|-0.3|0.7,0
min_x1,GE,1|0|0|0|0|0,5
min_x4,GE,0|0|0|1|0|0,3
max_evening_ratio,LE,-0.25|-0.25|-0.25|-0.25|0.75|0.75,0
EOF

# Create the solver_output.dat file
RUN cat <<EOF > /home/user/audit/solver_output.dat
x1 = 10.0
x2 = 8.0
x3 = 7.0
x4 = 6.0
x5 = 4.0
x6 = 5.0
EOF

# Set permissions on the created files
RUN chmod 0666 /home/user/audit/constraints.csv && \
    chmod 0666 /home/user/audit/solver_output.dat

# Set working directory
WORKDIR /home/user
