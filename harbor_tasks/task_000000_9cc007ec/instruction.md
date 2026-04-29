Pipeline's been failing for two weeks on the post-build asset cleanup — supposed to delete all the intermediate `.dSYM` bundles older than 7 days from `/home/user/builds` recursively, but only the ones that don't have a matching `.ipa` still present (we keep symbols for active releases). Script's at `/home/user/scripts/cleanup.sh`, been running it manually and it either deletes nothing or nukes everything including the ones we need.

Logs show it's definitely finding files, then either the `xargs rm -rf` gets nothing or it gets way too much. I added some debug output but honestly I'm more confused now. The filenames have spaces and build metadata in them which might be part of it? But the `find` command looks fine to me.

Need this working before tonight's nightly or we're gonna blow past the disk quota again.
