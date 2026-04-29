FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/optim && chmod 0777 /home/user && chmod 0777 /home/user/optim

RUN cat <<EOF > /home/user/optim/cplex.prm
CPXPARAM_TimeLimit 3600
CPXPARAM_Threads 4
CPXPARAM_MIP_Tolerances_MIPGap 0.01
CPXPARAM_MIP_Strategy_File 2
CPXPARAM_Preprocessing_Presolve 1
EOF

RUN chmod 0666 /home/user/optim/cplex.prm

CMD ["/bin/bash"]
