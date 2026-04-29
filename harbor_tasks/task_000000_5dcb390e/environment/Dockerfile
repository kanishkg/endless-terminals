FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0777 /home/user

WORKDIR /home/user/project

RUN mkdir -p /home/user/project/scripts

RUN cat > /home/user/project/package.json << 'EOF'
{
  "name": "test-project",
  "version": "2.4.0",
  "description": "Test project for standard-version",
  "main": "index.js",
  "scripts": {
    "release": "./scripts/release.sh"
  },
  "devDependencies": {
    "standard-version": "^9.5.0"
  }
}
EOF

RUN cat > /home/user/project/.versionrc.json << 'EOF'
{
  "types": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"}
  ],
  "tagPrefix": "v",
  "bumpFiles": [
    {
      "filename": "package.json",
      "type": "json"
    },
    {
      "filename": "VERSION",
      "type": "plain-text"
    }
  ]
}
EOF

RUN echo "v2.4.0" > /home/user/project/VERSION

RUN cat > /home/user/project/CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

## [2.4.0](https://github.com/example/project/compare/v2.3.0...v2.4.0) (2024-01-15)

### Features

* add new logging system ([abc1234](https://github.com/example/project/commit/abc1234))

### Bug Fixes

* resolve memory leak in parser ([def5678](https://github.com/example/project/commit/def5678))

## [2.3.0](https://github.com/example/project/compare/v2.2.0...v2.3.0) (2024-01-01)

### Features

* initial release features ([ghi9012](https://github.com/example/project/commit/ghi9012))
EOF

RUN cat > /home/user/project/scripts/release.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
npx standard-version --release-as minor
EOF

RUN chmod +x /home/user/project/scripts/release.sh

RUN npm install --prefix /home/user/project

RUN git config --global user.name "Test User" && \
    git config --global user.email "test@example.com" && \
    git config --global init.defaultBranch main

RUN cd /home/user/project && \
    git init && \
    git add package.json .versionrc.json CHANGELOG.md scripts/release.sh && \
    git commit -m "chore: initial commit" && \
    git add VERSION && \
    git commit -m "chore: add VERSION file" && \
    git tag v2.4.0 && \
    echo "// placeholder" > index.js && \
    git add index.js && \
    git commit -m "feat: add backup rotation policy" && \
    echo "// another placeholder" > utils.js && \
    git add utils.js && \
    git commit -m "fix: correct archive timestamp format"

RUN chown -R root:root /home/user/project && \
    chmod -R 0777 /home/user/project && \
    chmod -R 0777 /home/user

WORKDIR /home/user

CMD ["/bin/bash"]
