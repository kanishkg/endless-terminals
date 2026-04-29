Rotating creds on the auth service and the re-encryption job at /home/user/rotate/reencrypt.py is glacially slow — like 45+ minutes to churn through the vault export at /home/user/rotate/vault_dump.enc. It's ~80k entries, each one AES-256-GCM encrypted with the old key, needs to be decrypted and re-encrypted with the new key, then written out to vault_dump.new.enc.

The script works correctly afaict, checksums match when I spot-check, but 45 minutes for 80k records is absurd. Old key and new key are in /home/user/rotate/old.key and /home/user/rotate/new.key. I figured it was just python crypto overhead but even with pycryptodome it shouldn't be this bad? Maybe I'm doing something dumb with the file format.

Need this under 60 seconds without breaking the output format — ops has tooling downstream that parses the .enc files and I do NOT want to debug that at 2am.
