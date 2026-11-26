#!/usr/bin/env python3
"""make.fun entry: "Sum up 26 November's world news in one image" (v2).

The entry image is pre-rendered and shipped in this repository as
entry.png. This program copies it into the grader's output directory.

Deterministic by construction: a fixed file copy, no clock, no random
numbers, no network, no environment-dependent behaviour. It writes
exactly one file, <output>/entry.png, and exits 0.
"""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, "entry.png")


def run():
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    shutil.copyfile(SOURCE, os.path.join(target_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(run())
