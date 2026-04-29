FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    coreutils \
    findutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /var/data/logs /var/data/cache /var/data/uploads /var/data/tmp

RUN dd if=/dev/zero of=/var/data/logs/app.log.2024-01-15 bs=1M count=247

RUN dd if=/dev/zero of=/var/data/logs/debug.log bs=1M count=189

RUN dd if=/dev/zero of=/var/data/cache/thumbnails.db bs=1M count=312

RUN dd if=/dev/zero of=/var/data/uploads/video_backup.tar bs=1M count=524

RUN dd if=/dev/zero of=/var/data/tmp/core.1847 bs=1M count=156

RUN dd if=/dev/zero of=/var/data/logs/access.log bs=1M count=50

RUN dd if=/dev/zero of=/var/data/logs/error.log bs=1M count=25

RUN dd if=/dev/zero of=/var/data/cache/session_cache.dat bs=1M count=75

RUN dd if=/dev/zero of=/var/data/cache/query_cache.db bs=1M count=30

RUN dd if=/dev/zero of=/var/data/uploads/image001.jpg bs=1K count=512

RUN dd if=/dev/zero of=/var/data/uploads/image002.png bs=1K count=1024

RUN dd if=/dev/zero of=/var/data/uploads/document.pdf bs=1M count=5

RUN dd if=/dev/zero of=/var/data/tmp/temp_file.tmp bs=1M count=10

RUN dd if=/dev/zero of=/var/data/tmp/swap.dat bs=1M count=45

RUN echo "config data" > /var/data/config.ini

RUN echo "readme content" > /var/data/README.txt

RUN chmod -R 755 /var/data

RUN useradd -m -d /home/user -s /bin/bash user

RUN chown -R user:user /home/user

CMD ["/bin/bash"]
