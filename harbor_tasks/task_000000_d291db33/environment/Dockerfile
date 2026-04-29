FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    rsync \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/bin && \
    mkdir -p /home/user/remote-docs/archive && \
    mkdir -p /home/user/local-docs

RUN head -c 1024 /dev/urandom | base64 | head -c 1024 > /home/user/remote-docs/notes.txt

RUN head -c 2097152 /dev/urandom > /home/user/remote-docs/report.pdf

RUN head -c 8388608 /dev/urandom > /home/user/remote-docs/slides.pptx

RUN head -c 125829120 /dev/urandom > /home/user/remote-docs/training-video.mp4

RUN head -c 500 /dev/urandom | base64 | head -c 500 > /home/user/remote-docs/archive/old-notes.txt

RUN head -c 78643200 /dev/urandom > /home/user/remote-docs/archive/demo-recording.mov

RUN chmod 644 /home/user/remote-docs/notes.txt && \
    chmod 640 /home/user/remote-docs/report.pdf && \
    chmod 644 /home/user/remote-docs/slides.pptx && \
    chmod 644 /home/user/remote-docs/training-video.mp4 && \
    chmod 644 /home/user/remote-docs/archive/old-notes.txt && \
    chmod 644 /home/user/remote-docs/archive/demo-recording.mov

RUN touch -d "2024-01-15 10:00:00" /home/user/remote-docs/notes.txt && \
    touch -d "2024-02-20 14:30:00" /home/user/remote-docs/report.pdf && \
    touch -d "2024-03-01 09:15:00" /home/user/remote-docs/slides.pptx && \
    touch -d "2024-03-05 16:00:00" /home/user/remote-docs/training-video.mp4 && \
    touch -d "2023-06-10 08:00:00" /home/user/remote-docs/archive/old-notes.txt && \
    touch -d "2023-07-22 11:30:00" /home/user/remote-docs/archive/demo-recording.mov

RUN chmod 0777 /home/user && \
    chmod 0777 /home/user/bin && \
    chmod 0777 /home/user/local-docs && \
    chmod 0755 /home/user/remote-docs && \
    chmod 0755 /home/user/remote-docs/archive

WORKDIR /home/user

CMD ["/bin/bash"]
