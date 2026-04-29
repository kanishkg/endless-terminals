Building an archiving pipeline at /home/user/archive_pipeline — it's supposed to take a directory tree, compress it into a custom .carch bundle (tar | zstd internally, with a metadata header), then extract it back out elsewhere and verify checksum. The create step works fine, but extract is silently corrupting files. Specifically the restored tree passes the directory structure check but content checksums fail on maybe 30% of files, seemingly random which ones.

Thought maybe the zstd stream wasn't flushing, but I've stared at that for an hour and it looks fine. The header parsing also seems right — I print out the metadata and it matches. The weird part is if I manually run `tar -I zstd -xf` on the payload portion after skipping the header, everything extracts correctly. So the data's fine, something in my extraction code is mangling it.

Need extract.py fixed so `./run_test.sh` passes — it creates a test tree, round-trips it, and compares sha256 of every file.
