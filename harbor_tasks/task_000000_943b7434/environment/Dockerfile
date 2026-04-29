FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/data && chmod 0777 /home/user && chmod 0777 /home/user/data

RUN dd if=/dev/urandom bs=1M count=50 | gzip > /home/user/data/imagenet_subset.tar.gz && \
    chmod 644 /home/user/data/imagenet_subset.tar.gz

RUN cd /home/user/data && sha256sum imagenet_subset.tar.gz > imagenet_subset.sha256 && \
    chmod 644 /home/user/data/imagenet_subset.sha256

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
