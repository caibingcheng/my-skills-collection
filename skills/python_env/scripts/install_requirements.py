#!/usr/bin/env python3
"""Install requirements into an existing virtual environment.

Example:
  python install_requirements.py --venv .venv --requirements requirements.txt
"""
import argparse
import os
import subprocess
import sys


def run(cmd, **kwargs):
    print(f">>> {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)


def main():
    p = argparse.ArgumentParser(description="Install requirements into venv")
    p.add_argument("--venv", required=True, help="Path to virtualenv directory")
    p.add_argument("--requirements", default="requirements.txt", help="Requirements file")
    p.add_argument("--upgrade-pip", action="store_true", help="Upgrade pip before installing")
    args = p.parse_args()

    venv_path = os.path.abspath(args.venv)
    pip = os.path.join(venv_path, "bin", "pip")
    py = os.path.join(venv_path, "bin", "python")

    if not os.path.exists(pip):
        print(f"pip not found in venv: {pip}")
        sys.exit(2)

    if args.upgrade_pip:
        run([py, "-m", "pip", "install", "--upgrade", "pip"])

    if not os.path.exists(args.requirements):
        print(f"requirements file not found: {args.requirements}")
        sys.exit(2)

    run([pip, "install", "-r", args.requirements])


if __name__ == "__main__":
    main()
