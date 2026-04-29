FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/webapp && chmod 0777 /home/user && chmod 0777 /home/user/webapp

RUN cat > /home/user/webapp/requirements.txt << 'EOF'
flask
requests
click
EOF

RUN chmod 644 /home/user/webapp/requirements.txt

RUN python3 -m venv /home/user/webapp/venv

RUN /home/user/webapp/venv/bin/pip install --upgrade pip

RUN /home/user/webapp/venv/bin/pip install flask==2.3.2 requests==2.31.0 click==8.1.3

RUN chmod -R 0777 /home/user/webapp

WORKDIR /home/user

CMD ["/bin/bash"]
