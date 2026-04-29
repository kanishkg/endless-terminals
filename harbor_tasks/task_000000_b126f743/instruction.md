Build artifacts in /home/user/artifacts are getting corrupted during our nightly compress-and-archive pipeline. The script at /home/user/scripts/archive.sh takes a directory, tars it, compresses with gzip, then splits into 50MB chunks for our artifact store. Downstream, /home/user/scripts/restore.sh reassembles and extracts.

Problem is restore.sh fails with "gzip: stdin: not in gzip format" — but only sometimes. I ran it five times this morning, failed three times, worked twice. Same input files. The archive.sh script hasn't changed in months and the checksums on the split chunks match between runs, so the chunks themselves aren't getting corrupted in storage.

I threw a known-good test directory at it in /home/user/test_payload (just some binaries and logs, ~180MB total). Can you figure out what's going wrong? Need both scripts working reliably — archive should produce chunks, restore should reconstruct the original directory exactly.
