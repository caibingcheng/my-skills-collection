#!/usr/bin/env python3
"""Remove a skill from ~/.my-skills-collection, handling submodules or copied dirs.

Usage:
  python remove_skill.py --name skill-name
"""
import argparse
import os
import shutil
import subprocess
import sys


def run(cmd):
    print('>>>', ' '.join(cmd))
    subprocess.check_call(cmd)


def confirm(prompt):
    resp = input(prompt + ' [y/N]: ').strip().lower()
    return resp == 'y'


def remove_submodule(name, repo_root):
    path = os.path.join('skills', name)
    run(['git', 'submodule', 'deinit', '-f', path])
    run(['rm', '-rf', os.path.join('.git', 'modules', path)])
    run(['git', 'rm', '-f', path])
    run(['git', 'commit', '-m', f'Remove skill {name} submodule'])


def remove_copied(name, repo_root):
    target = os.path.join(repo_root, 'skills', name)
    if not os.path.exists(target):
        print('Not found:', target)
        sys.exit(1)
    shutil.rmtree(target)
    run(['git', 'add', '-u', os.path.join('skills', name)])
    run(['git', 'commit', '-m', f'Remove skill {name}'])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--name', required=True, help='Name of skill to remove')
    p.add_argument('--repo-root', default=os.path.expanduser('~/.my-skills-collection'))
    args = p.parse_args()

    if not confirm(f'Confirm removal of skill "{args.name}" from {args.repo_root}?'):
        print('Aborted')
        return

    # detect submodule
    submodule_path = os.path.join(args.repo_root, 'skills', args.name)
    gitmodules = os.path.join(args.repo_root, '.gitmodules')
    if os.path.exists(gitmodules):
        with open(gitmodules, 'r') as f:
            if args.name in f.read():
                remove_submodule(args.name, args.repo_root)
                return

    remove_copied(args.name, args.repo_root)


if __name__ == '__main__':
    main()
