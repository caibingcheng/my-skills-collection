#!/usr/bin/env python3
"""Create a Python virtual environment and optionally install requirements.

Usage examples:
  python create_venv.py --path /tmp/myenv --upgrade-pip
  python create_venv.py --path .venv --requirements requirements.txt
"""
import argparse
import os
import subprocess
import sys
import venv


def run(cmd, **kwargs):
    print(f">>> {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)


def main():
    p = argparse.ArgumentParser(description="Create venv and optionally install requirements")
    p.add_argument("--path", required=True, help="Path to create venv")
    p.add_argument("--python", help="Python executable to use (e.g. python3.11)")
    p.add_argument("--upgrade-pip", action="store_true", help="Upgrade pip after creating venv")
    p.add_argument("--requirements", help="Path to requirements.txt to install into the venv")
    args = p.parse_args()

    venv_path = os.path.abspath(args.path)
    if os.path.exists(venv_path) and os.listdir(venv_path):
        print(f"Warning: {venv_path} exists and is not empty")

    builder = venv.EnvBuilder(with_pip=True)
    print(f"Creating venv at {venv_path}...")
    builder.create(venv_path)

    py = os.path.join(venv_path, "bin", "python")
    pip = os.path.join(venv_path, "bin", "pip")

    if args.upgrade_pip:
        run([py, "-m", "pip", "install", "--upgrade", "pip"])

    if args.requirements:
        if not os.path.exists(args.requirements):
            print(f"requirements file not found: {args.requirements}")
            sys.exit(2)
        run([pip, "install", "-r", args.requirements])

    print("\nActivation commands:")
    print(f"bash/zsh: source {venv_path}/bin/activate")
    print(f"fish: source {venv_path}/bin/activate.fish")
    print(f"Windows (cmd): {venv_path}\\Scripts\\activate.bat")
    print(f"Windows (PowerShell): {venv_path}\\Scripts\\Activate.ps1")


if __name__ == "__main__":
    main()
