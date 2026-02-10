#!/usr/bin/env python3
"""Add a skill to ~/.my-skills-collection either as a git submodule or by copying a directory.

Examples:
  python add_skill.py --submodule https://github.com/owner/skill.git --name skill-name
  python add_skill.py --copy /path/to/skill --name skill-name
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


def add_submodule(repo_url, name, repo_root):
    target = os.path.join(repo_root, 'skills', name)
    if os.path.exists(target):
        print('Target already exists:', target)
        sys.exit(1)
    run(['git', 'submodule', 'add', repo_url, target])
    run(['git', 'commit', '-m', f'Add skill {name} as submodule'])


def copy_skill(src, name, repo_root):
    dest = os.path.join(repo_root, 'skills', name)
    if os.path.exists(dest):
        print('Target already exists:', dest)
        sys.exit(1)
    shutil.copytree(src, dest)
    run(['git', 'add', os.path.join('skills', name)])
    run(['git', 'commit', '-m', f'Add skill {name} (copied)'])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--submodule', help='Git URL to add as submodule')
    p.add_argument('--copy', help='Local path to copy into skills/')
    p.add_argument('--name', required=True, help='Name for the skill directory')
    p.add_argument('--repo-root', default=os.path.expanduser('~/.my-skills-collection'))
    args = p.parse_args()

    if not (args.submodule or args.copy):
        print('Specify --submodule or --copy')
        sys.exit(2)

    if not confirm(f'Proceed to add skill "{args.name}" to {args.repo_root}?'):
        print('Aborted')
        return

    if args.submodule:
        add_submodule(args.submodule, args.name, args.repo_root)
    else:
        if not os.path.exists(args.copy):
            print('Source not found:', args.copy)
            sys.exit(2)
        copy_skill(args.copy, args.name, args.repo_root)


if __name__ == '__main__':
    main()
