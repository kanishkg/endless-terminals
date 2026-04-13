I'm an integration developer and I need to test our API's ability to handle GPG-encrypted and signed payloads. Can you help me set up a quick test scenario?

First, I need you to create a GPG key pair for testing purposes. Use the following details:
- Name: "API Test User"
- Email: "apitest@example.com"
- No passphrase (for automated testing)
- Key type: RSA
- Key size: 2048 bits

Once the key is created, I have a test API payload file at `/home/user/api_payload.json` that I need you to work with.

Please do the following:

1. Create a detached signature for the file `/home/user/api_payload.json` and save it as `/home/user/api_payload.json.sig`

2. Encrypt the file `/home/user/api_payload.json` using the GPG key you created (encrypt for "apitest@example.com") and save the encrypted file as `/home/user/api_payload.json.gpg`

3. Verify the detached signature you created and decrypt the encrypted file to confirm everything works correctly.

4. Create a verification log file at `/home/user/gpg_test_results.log` with the following exact format:
```
KEY_FINGERPRINT=<the full 40-character fingerprint of the created key>
SIGNATURE_VALID=<YES or NO>
DECRYPTION_SUCCESSFUL=<YES or NO>
ORIGINAL_HASH=<sha256sum of the original api_payload.json file, just the hash>
DECRYPTED_HASH=<sha256sum of the decrypted content, just the hash>
```

The hashes should match if encryption/decryption worked correctly. Make sure all the values are on their own lines with no extra spaces around the equals sign.
