FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    gnupg \
    python3 \
    python3-pip \
    file \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/artifacts && chmod 0777 /home/user && chmod 0777 /home/user/artifacts

RUN dd if=/dev/urandom of=/tmp/model_weights bs=1 count=1024

RUN echo "artifact2024" | gpg --batch --yes --passphrase-fd 0 --symmetric --cipher-algo AES256 -o /home/user/artifacts/model_weights.gpg /tmp/model_weights && rm /tmp/model_weights

RUN chmod 0666 /home/user/artifacts/model_weights.gpg

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
