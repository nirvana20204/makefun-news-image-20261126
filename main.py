#!/usr/bin/env python3
"""make.fun entry for "Sum up 25 November's world news in one image".

The entry image is pre-rendered and shipped in this repository as
entry.png. This program copies it to the grader's output directory.

Deterministic by construction: a fixed file copy. No wall-clock time,
no randomness, no network access, no environment-dependent behaviour.
Writes exactly one file: <output>/entry.png. Exits 0.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
