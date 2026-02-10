#!/usr/bin/env python3
"""Sync the my-skills-collection repository and update submodules safely.

Usage:
  python sync_repo.py
"""
import os
import subprocess
import sys


def run(cmd):
    print('>>>', ' '.join(cmd))
    subprocess.check_call(cmd)


def main():
    repo_root = os.path.expanduser('~/.my-skills-collection')
    if not os.path.exists(repo_root):
        print('Repository not found:', repo_root)
        sys.exit(1)

    # Ensure working tree is clean
    run(['git', '-C', repo_root, 'add', '.'])
    try:
        run(['git', '-C', repo_root, 'commit', '-m', 'Save current changes before sync'])
    except subprocess.CalledProcessError:
        print('No changes to commit (or commit failed). Continuing...')

    run(['git', '-C', repo_root, 'pull', 'origin', 'main'])
    run(['git', '-C', repo_root, 'submodule', 'update', '--remote', '--merge'])

    print('Sync complete. Review changes and resolve conflicts if any.')


if __name__ == '__main__':
    main()
