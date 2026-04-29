Git hook system on /home/user/infra-configs is acting weird — pre-commit hook is supposed to block commits that add world-readable private keys (mode 0644 or looser on files matching `*.pem` or `*.key`), but someone just pushed a commit with a 0644 key file and the hook apparently didn't fire. I checked and `.git/hooks/pre-commit` exists and is executable, ran `git config core.hooksPath` and it's unset, so it should be using the repo's hooks dir.

The thing is, when I test it locally by staging a bad key file and running `git commit`, it blocks me fine. So the hook works? But the commit history shows the bad file got in somehow. Commit is 3 days old, made by jenkins-bot according to the author. Nobody's touched the hook since before that.

Need to figure out how the bad commit bypassed the hook and harden the setup so it can't happen again. The fix should be in place in that repo — whatever config or hook changes needed.
