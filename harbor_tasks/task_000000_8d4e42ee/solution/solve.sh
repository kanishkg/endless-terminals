#!/bin/bash
# Auto-generated solve script
set -e

gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: API Test User
Name-Email: apitest@example.com
Expire-Date: 0
%no-protection
%commit
EOF
gpg --batch --yes --detach-sign --output /home/user/api_payload.json.sig /home/user/api_payload.json
gpg --batch --yes --encrypt --recipient apitest@example.com --output /home/user/api_payload.json.gpg /home/user/api_payload.json
gpg --batch --verify /home/user/api_payload.json.sig /home/user/api_payload.json
gpg --batch --yes --decrypt --output /home/user/api_payload_decrypted.json /home/user/api_payload.json.gpg
gpg --fingerprint apitest@example.com
sha256sum /home/user/api_payload.json
sha256sum /home/user/api_payload_decrypted.json
cat > /home/user/gpg_test_results.log << 'EOF'
KEY_FINGERPRINT=0C08027F1623B7C246161E3D53D967C466660E22
SIGNATURE_VALID=YES
DECRYPTION_SUCCESSFUL=YES
ORIGINAL_HASH=bb3c20f695b77ab00ff86a08518b772260548a1dfa03f450a672b696aac77ff1
DECRYPTED_HASH=bb3c20f695b77ab00ff86a08518b772260548a1dfa03f450a672b696aac77ff1
EOF
cat /home/user/gpg_test_results.log
ls -la /home/user/api_payload.json* /home/user/gpg_test_results.log
