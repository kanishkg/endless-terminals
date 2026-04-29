Our CI started choking on `/home/user/myapp` yesterday — `pip install -e .` works fine, but when the build tries `pip wheel . -w dist/` it dies with some resolver error about conflicting versions of urllib3. Thing is, we haven't touched dependencies in weeks and the lockfile hasn't changed. Might be something with how extras are declared? We have a `[dev]` extra that pulls in different testing stuff.

Anyway need the wheel build working. The package should still be installable with `pip install myapp[dev]` after you fix it — we use that in CI for the test stage.
