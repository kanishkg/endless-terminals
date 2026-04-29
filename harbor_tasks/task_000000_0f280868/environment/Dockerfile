FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    patch \
    diffutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/mldata/samples && \
    mkdir -p /home/user/mldata/output && \
    chmod -R 0777 /home/user/mldata

RUN cat << 'EOF' > /home/user/mldata/expected.txt
sample_001: Hello world
sample_002: Goodbye world
sample_003: The quick brown fox jumps over the lazy dog
sample_004: Machine learning is transforming industries
sample_005: Data quality matters more than model size
EOF

RUN cat << 'PYEOF' > /home/user/mldata/apply_patches.py
#!/usr/bin/env python3
"""
Apply patches from samples/ directory and write results to output/
"""

import os
import glob

BASE_DIR = "/home/user/mldata"
SAMPLES_DIR = os.path.join(BASE_DIR, "samples/")
OUTPUT_DIR = os.path.join(BASE_DIR, "output/")


def apply_patch(original, patch):
    """Apply a unified diff patch to original text."""
    lines = original.split('\n')
    result = lines[:]
    in_hunk = False
    pos = 0  # BUG: always starts at 0, ignores @@ -X,Y +A,B @@
    for pline in patch.split('\n'):
        if pline.startswith('@@'):
            in_hunk = True
            pos = 0  # should parse the +A from header and set pos = A - 1
            continue
        if in_hunk:
            if pline.startswith('-'):
                if pos < len(result):
                    result.pop(pos)
            elif pline.startswith('+'):
                result.insert(pos, pline[1:])
                pos += 1
            elif pline.startswith(' '):
                pos += 1
    return '\n'.join(result)


def main():
    # Find all .txt files in samples directory
    txt_files = glob.glob(os.path.join(SAMPLES_DIR, "*.txt"))

    for txt_path in sorted(txt_files):
        basename = os.path.basename(txt_path)
        name = basename.replace('.txt', '')
        patch_path = os.path.join(SAMPLES_DIR, f"{name}.patch")

        if not os.path.exists(patch_path):
            print(f"Warning: No patch file for {name}")
            continue

        with open(txt_path, 'r') as f:
            original = f.read()

        with open(patch_path, 'r') as f:
            patch = f.read()

        result = apply_patch(original, patch)

        output_path = os.path.join(OUTPUT_DIR, basename)
        with open(output_path, 'w') as f:
            f.write(result)

        print(f"Processed {name}")

    return 0


if __name__ == "__main__":
    exit(main())
PYEOF

RUN chmod +x /home/user/mldata/apply_patches.py

RUN echo "Hllo world" > /home/user/mldata/samples/sample_001.txt

RUN cat << 'EOF' > /home/user/mldata/samples/sample_001.patch
--- sample_001.txt.orig	2024-01-01 00:00:00.000000000 +0000
+++ sample_001.txt	2024-01-01 00:00:01.000000000 +0000
@@ -1 +1 @@
-Hllo world
+Hello world
EOF

RUN echo "Godbye world" > /home/user/mldata/samples/sample_002.txt

RUN cat << 'EOF' > /home/user/mldata/samples/sample_002.patch
--- sample_002.txt.orig	2024-01-01 00:00:00.000000000 +0000
+++ sample_002.txt	2024-01-01 00:00:01.000000000 +0000
@@ -1 +1 @@
-Godbye world
+Goodbye world
EOF

RUN printf "Line one\nLine two\nLine three\nThe quick brown fox jumps over the lazy do\nLine five\n" > /home/user/mldata/samples/sample_003.txt

RUN cat << 'EOF' > /home/user/mldata/samples/sample_003.patch
--- sample_003.txt.orig	2024-01-01 00:00:00.000000000 +0000
+++ sample_003.txt	2024-01-01 00:00:01.000000000 +0000
@@ -1,5 +1 @@
-First line here
-Second line here
-Third line here
-The quick brown fox jumps over the lazy do
-Fifth line here
+The quick brown fox jumps over the lazy dog
EOF

RUN printf "Header line\nIntro paragraph\nMachine learning is transforming industrie\nConclusion here\n" > /home/user/mldata/samples/sample_004.txt

RUN cat << 'EOF' > /home/user/mldata/samples/sample_004.patch
--- sample_004.txt.orig	2024-01-01 00:00:00.000000000 +0000
+++ sample_004.txt	2024-01-01 00:00:01.000000000 +0000
@@ -1,4 +1 @@
-Some header
-Some intro
-Machine learning is transforming industrie
-Some conclusion
+Machine learning is transforming industries
EOF

RUN printf "Title goes here\nSubtitle line\nData quality matters more than model siz\nFooter text\n" > /home/user/mldata/samples/sample_005.txt

RUN cat << 'EOF' > /home/user/mldata/samples/sample_005.patch
--- sample_005.txt.orig	2024-01-01 00:00:00.000000000 +0000
+++ sample_005.txt	2024-01-01 00:00:01.000000000 +0000
@@ -1,4 +1 @@
-A title
-A subtitle
-Data quality matters more than model siz
-A footer
+Data quality matters more than model size
EOF

RUN chmod -R 0777 /home/user/mldata
