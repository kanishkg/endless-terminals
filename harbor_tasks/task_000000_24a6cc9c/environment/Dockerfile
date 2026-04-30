FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    sed \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/libmetrics && chmod 0777 /home/user && chmod 0777 /home/user/libmetrics

RUN cat <<'EOF' > /home/user/libmetrics/package.json
{
  "name": "libmetrics",
  "version": "2.3.1",
  "description": "A metrics library for monitoring applications",
  "main": "index.js",
  "scripts": {
    "test": "jest",
    "build": "tsc"
  },
  "dependencies": {
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "typescript": "^5.0.0"
  },
  "author": "Metrics Team",
  "license": "MIT"
}
EOF

RUN cat <<'EOF' > /home/user/libmetrics/CHANGELOG.md
# Changelog

## [2.3.1] - 2024-09-15
- Fixed memory leak in counter reset

## [2.3.0] - 2024-08-22
- Added gauge metric type
- Improved thread safety
EOF

RUN chmod 0666 /home/user/libmetrics/package.json && chmod 0666 /home/user/libmetrics/CHANGELOG.md

WORKDIR /home/user

CMD ["/bin/bash"]
