FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    bash \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/mobile-ci/scripts && \
    mkdir -p /home/user/mobile-ci/config

RUN cat > /home/user/mobile-ci/scripts/build.sh << 'EOF'
#!/bin/bash
set -e

# Load environment
set -a
source /home/user/mobile-ci/config/base.env
source /home/user/mobile-ci/config/ci.env
set +a

# Legacy compatibility shim
export CODE_SIGN_IDENTITY="${CODE_SIGN_IDENTITY:-}"
export PROVISIONING_PROFILE_SPECIFIER="$PROFILE_SPEC"

# Run build
exec /home/user/mobile-ci/scripts/fastlane_stub.sh
EOF

RUN chmod +x /home/user/mobile-ci/scripts/build.sh

RUN cat > /home/user/mobile-ci/scripts/fastlane_stub.sh << 'EOF'
#!/bin/bash
# Stub for fastlane gym
if [ -z "$CODE_SIGN_IDENTITY" ]; then
    echo "Error: Missing required signing identity" >&2
    echo "Searched for identity matching: ''" >&2
    exit 1
fi

if [ -z "$PROVISIONING_PROFILE_SPECIFIER" ]; then
    echo "Error: Missing provisioning profile" >&2
    exit 1
fi

echo "Build succeeded with identity: $CODE_SIGN_IDENTITY"
echo "Using profile: $PROVISIONING_PROFILE_SPECIFIER"
echo "Team: $TEAM_ID"
echo "Bundle: $BUNDLE_ID"
exit 0
EOF

RUN chmod +x /home/user/mobile-ci/scripts/fastlane_stub.sh

RUN cat > /home/user/mobile-ci/config/base.env << 'EOF'
CODE_SIGN_IDENTITY="iPhone Distribution: ACME Corp (ABC123)"
PROFILE_SPEC=ACME_AppStore_Profile
TEAM_ID=ABC123XYZ
BUNDLE_ID=com.acme.app
EOF

RUN cat > /home/user/mobile-ci/config/ci.env << 'EOF'
# CI-specific overrides
PROFILE_SPEC=ACME_CI_Profile
BUILD_NUMBER=${BUILD_NUMBER:-1}

# Reset identity for CI cert selection
CODE_SIGN_IDENTITY=
EOF

RUN chmod -R 0777 /home/user/mobile-ci

WORKDIR /home/user

CMD ["/bin/bash"]
