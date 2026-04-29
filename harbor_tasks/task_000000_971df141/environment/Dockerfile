FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/captures/session1 \
    && mkdir -p /home/user/captures/session2/tuesday \
    && mkdir -p /home/user/captures/session2/wednesday \
    && mkdir -p /home/user/captures/old/backup/deep \
    && mkdir -p /home/user/captures/misc

RUN dd if=/dev/urandom of=/home/user/captures/session1/trace_001.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/session1/trace_002.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/session1/trace_003.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/session2/trace_004.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/session2/tuesday/trace_005.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/session2/tuesday/trace_006.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/session2/wednesday/trace_007.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/old/trace_008.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/old/backup/trace_009.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/old/backup/trace_010.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/old/backup/deep/trace_011.perf bs=1024 count=1 2>/dev/null \
    && dd if=/dev/urandom of=/home/user/captures/misc/trace_012.perf bs=1024 count=1 2>/dev/null

RUN chmod -R 0777 /home/user/captures

WORKDIR /home/user

CMD ["/bin/bash"]
