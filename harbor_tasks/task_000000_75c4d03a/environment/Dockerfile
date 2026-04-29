FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    rsync \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/project/src && \
    mkdir -p /home/user/project/config && \
    mkdir -p /home/user/backup

RUN echo -n "# Project" > /home/user/project/README.md
RUN echo -n "print('hello')" > /home/user/project/src/main.py
RUN echo -n "API_KEY=secret123" > /home/user/project/.env
RUN echo -n "*.pyc" > /home/user/project/.gitignore
RUN echo -n "hidden config" > /home/user/project/config/.hidden

RUN printf '%s\n' '--exclude=.*' '--archive' > /home/user/.rsyncrc

RUN chmod -R 0777 /home/user/project && \
    chmod -R 0777 /home/user/backup && \
    chmod 0666 /home/user/.rsyncrc

WORKDIR /home/user
