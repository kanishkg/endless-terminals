Got a weird one. /home/user/project has a Makefile that's supposed to build three targets — `lib`, `app`, and `docs` — and there's a `make all` that should build them in dependency order. Thing is, `make -j4 all` deadlocks maybe 60% of the time, but `make all` (sequential) always works. And `make -j4 lib app docs` typed out explicitly also works fine, every time.

So it's not the individual recipes, it's something about how `all` interacts with parallel make. I've stared at the dependency declarations for an hour and they look correct to me. There's a .PHONY line, deps look right, no cycles that I can see.

Need `make -j4 all` to reliably complete. The build artifacts should end up the same as the sequential build — lib/libfoo.a, bin/app, docs/manual.html.
