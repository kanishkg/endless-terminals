FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    git \
    build-essential \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN useradd -m -d /home/user -s /bin/bash user

RUN mkdir -p /home/user/mlservice && chown -R user:user /home/user/mlservice

RUN pip3 install tokenizers==0.13.3

RUN cat > /home/user/mlservice/__init__.py << 'INITEOF'
from transformers import AutoTokenizer
def run():
    tok = AutoTokenizer.from_pretrained("bert-base-uncased")
    print(f"Tokenizer loaded: {type(tok).__name__}")
INITEOF

RUN cat > /home/user/mlservice/__main__.py << 'MAINEOF'
from mlservice import run
run()
MAINEOF

RUN cat > /home/user/mlservice/requirements.txt << 'REQEOF'
transformers==4.36.0
tokenizers==0.15.0
torch==2.1.0
numpy==1.26.0
REQEOF

RUN cat > /home/user/.bashrc << 'BASHRCEOF'
# ~/.bashrc: executed by bash(1) for non-login shells.

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# some useful aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Python alias - using system python for consistency
alias python='/usr/bin/python3'

# enable color support of ls
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
fi
BASHRCEOF

RUN chown user:user /home/user/.bashrc && chmod 644 /home/user/.bashrc

RUN chown -R user:user /home/user/mlservice

USER user
WORKDIR /home/user/mlservice

RUN python3.11 -m venv /home/user/mlservice/.venv

RUN /home/user/mlservice/.venv/bin/pip install --upgrade pip

RUN /home/user/mlservice/.venv/bin/pip install transformers==4.36.0 tokenizers==0.15.0 numpy==1.26.0

RUN /home/user/mlservice/.venv/bin/pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu || /home/user/mlservice/.venv/bin/pip install torch==2.1.0

USER root
RUN chown -R user:user /home/user
RUN chmod -R 755 /home/user/mlservice/.venv

USER user
WORKDIR /home/user

CMD ["/bin/bash"]
