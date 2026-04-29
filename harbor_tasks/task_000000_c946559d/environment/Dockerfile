FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    bash \
    python3 \
    python3-pip \
    sed \
    grep \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/release && chmod 0777 /home/user && chmod 0777 /home/user/release

RUN cat > /home/user/release/bump.sh << 'ENDSCRIPT'
#!/bin/bash
set -e

TARGET_VERSION="$1"

if [[ ! "$TARGET_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Usage: $0 <version>" >&2
    exit 1
fi

CURRENT=$(cat VERSION | tr -d '\n')
PREV_FROM_CHANGELOG=$(grep -E '## \[[0-9]' CHANGELOG.md | head -1 | sed -E 's/.*\[([0-9]+\.[0-9]+\.[0-9]+)\].*/\1/')

if [[ "$PREV_FROM_CHANGELOG" != "$CURRENT" ]]; then
    echo "invalid version format: changelog says '$PREV_FROM_CHANGELOG' but VERSION says '$CURRENT'" >&2
    exit 1
fi

# Update VERSION file
echo "$TARGET_VERSION" > VERSION

# Get today's date
TODAY=$(date +%Y-%m-%d)

# Update CHANGELOG.md
# 1. Replace the first ## [Unreleased] with new unreleased + the versioned section
sed -i "s/## \[Unreleased\]/## [Unreleased]\n\n## [$TARGET_VERSION] - $TODAY/" CHANGELOG.md

echo "Bumped to $TARGET_VERSION"
ENDSCRIPT

RUN chmod +x /home/user/release/bump.sh

RUN printf '2.3.0\n' > /home/user/release/VERSION

RUN cat > /home/user/release/CHANGELOG.md << 'ENDCHANGELOG'
# Changelog

## [Unreleased]

### Added
- New monitoring dashboard
- API rate limiting

## [2.3.0 ] - 2024-11-15

### Fixed
- Memory leak in worker pool

## [2.2.0] - 2024-10-01

### Added
- Initial metrics endpoint
ENDCHANGELOG

RUN chmod 0666 /home/user/release/VERSION && \
    chmod 0666 /home/user/release/CHANGELOG.md && \
    chmod 0755 /home/user/release/bump.sh

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
