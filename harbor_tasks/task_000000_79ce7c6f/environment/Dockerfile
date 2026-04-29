FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/webapp && chmod 0777 /home/user && chmod 0777 /home/user/webapp

RUN cat <<EOF > /home/user/webapp/requirements.txt
flask==2.3.3
gunicorn==21.2.0
EOF

RUN chmod 644 /home/user/webapp/requirements.txt

WORKDIR /home/user

CMD ["/bin/bash"]
