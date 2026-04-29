FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    make \
    pandoc \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/project/src \
    && mkdir -p /home/user/project/include \
    && mkdir -p /home/user/project/docs

RUN cat > /home/user/project/include/foo.h << 'EOF'
#ifndef FOO_H
#define FOO_H

int foo_func(int x);
int bar_func(int y);

#endif
EOF

RUN cat > /home/user/project/src/foo.c << 'EOF'
#include "foo.h"

int foo_func(int x) {
    return x * 2;
}
EOF

RUN cat > /home/user/project/src/bar.c << 'EOF'
#include "foo.h"

int bar_func(int y) {
    return y + 10;
}
EOF

RUN cat > /home/user/project/src/main.c << 'EOF'
#include <stdio.h>
#include "foo.h"

int main() {
    int a = foo_func(5);
    int b = bar_func(3);
    printf("foo_func(5) = %d\n", a);
    printf("bar_func(3) = %d\n", b);
    return 0;
}
EOF

RUN cat > /home/user/project/docs/manual.md << 'EOF'
# Project Manual

This is the manual for the project.

## Building

Run `make all` to build everything.

## Components

- **lib**: The static library libfoo.a
- **app**: The main application
- **docs**: This documentation
EOF

RUN cat > /home/user/project/Makefile << 'EOF'
.PHONY: all lib app docs clean

all: lib app docs

lib: lib/libfoo.a

lib/libfoo.a: src/foo.o src/bar.o
	@mkdir -p lib
	ar rcs $@ $^

app: bin/app

bin/app: src/main.o lib/libfoo.a
	@mkdir -p bin
	gcc -o $@ src/main.o -Llib -lfoo

docs: docs/manual.html

docs/manual.html: docs/manual.md
	pandoc -o $@ $<

src/%.o: src/%.c include/foo.h
	gcc -c -Iinclude -o $@ $<

clean:
	rm -rf lib bin src/*.o docs/manual.html
EOF

RUN chmod -R 0777 /home/user/project

WORKDIR /home/user

CMD ["/bin/bash"]
