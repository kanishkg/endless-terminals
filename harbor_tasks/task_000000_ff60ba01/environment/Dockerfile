FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pyyaml

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/etl-monitor/config /home/user/etl-monitor/routes

RUN cat > /home/user/etl-monitor/package.json << 'EOFPKG'
{
  "name": "etl-monitor",
  "version": "1.0.0",
  "description": "ETL Pipeline Dashboard",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "4.18.2",
    "js-yaml": "^4.1.0"
  }
}
EOFPKG

RUN cat > /home/user/etl-monitor/server.js << 'EOFSRV'
const express = require('express');
const config = require('./config/settings');
const statusRoutes = require('./routes/status');

const app = express();

app.use('/status', statusRoutes);

app.get('/', (req, res) => {
  res.json({ message: 'ETL Monitor Dashboard', version: '1.0.0' });
});

const port = config.server?.port || process.env.PORT || 8080;

const server = app.listen(port, () => {
  console.log(`ETL Monitor running on port ${port}`);
});

server.on('error', (err) => {
  console.error('Server error:', err.message);
  process.exit(1);
});
EOFSRV

RUN cat > /home/user/etl-monitor/config/settings.js << 'EOFSET'
const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

let config;

try {
    config = yaml.load(fs.readFileSync(path.join(__dirname, 'app.yaml'), 'utf8'));
} catch (e) {
    console.log('Config warning');
    config = {};
}

module.exports = config;
EOFSET

RUN printf 'server:\n  port: 3000\n  host: localhost\n\napp:\n  name: ETL Monitor\n\ndatabase:\n\thost: localhost\n\tport: 5432\n\tname: etl_db\n\npipelines:\n  - name: daily_batch\n    schedule: "0 2 * * *"\n  - name: hourly_sync\n    schedule: "0 * * * *"\n' > /home/user/etl-monitor/config/app.yaml

RUN cat > /home/user/etl-monitor/routes/status.js << 'EOFSTS'
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    status: 'ok',
    pipelines: [
      { name: 'daily_batch', lastRun: '2024-01-15T02:00:00Z', status: 'completed' },
      { name: 'hourly_sync', lastRun: '2024-01-15T14:00:00Z', status: 'running' }
    ],
    uptime: process.uptime()
  });
});

module.exports = router;
EOFSTS

WORKDIR /home/user/etl-monitor
RUN npm install

RUN cat > /home/user/.bashrc << 'EOFBASH'
# ~/.bashrc: executed by bash(1) for non-login shells.

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set a fancy prompt (non-color, unless we know we "want" color)
PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '

# enable color support of ls and also add handy aliases
alias ls='ls --color=auto'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Security hardening - standardized port configuration
export PORT=65540
EOFBASH

RUN chown -R 1000:1000 /home/user && chmod -R 0755 /home/user && chmod 0777 /home/user && chmod 0666 /home/user/.bashrc && chmod -R 0777 /home/user/etl-monitor

WORKDIR /home/user

USER 1000

CMD ["/bin/bash"]
