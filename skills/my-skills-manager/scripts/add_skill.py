#!/usr/bin/env python3
"""Add a skill to ~/.my-skills-collection either as a git submodule or by copying.

Examples:
  python add_skill.py --submodule https://github.com/owner/skill.git --name skill-name
  python add_skill.py --copy /path/to/skill --name skill-name
"""
import argparse
import os
import shutil
import subprocess
import sys


def run(cmd, cwd=None):
    """Run a command and return True if successful."""
    print('>>>', ' '.join(cmd))
    try:
        subprocess.check_call(cmd, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f'Error: Command failed with exit code {e.returncode}')
        return False


def is_git_repo(path):
    """Check if path is a git repository."""
    return os.path.exists(os.path.join(path, '.git'))


def confirm(prompt):
    """Ask for user confirmation."""
    try:
        resp = input(prompt + ' [y/N]: ').strip().lower()
        return resp == 'y'
    except EOFError:
        return False


def add_submodule(repo_url, name, repo_root):
    """Add a skill as a git submodule."""
    target = os.path.join(repo_root, 'skills', name)
    
    if os.path.exists(target):
        print(f'Error: Target already exists: {target}')
        sys.exit(1)
    
    if not run(['git', 'submodule', 'add', repo_url, target], cwd=repo_root):
        sys.exit(1)
    
    if not run(['git', 'commit', '-m', f'Add skill {name} as submodule'], cwd=repo_root):
        print('Warning: Commit failed. Check git status.')
    
    print(f'Successfully added {name} as submodule.')


def copy_skill(src, name, repo_root):
    """Copy a skill directory into the repository."""
    dest = os.path.join(repo_root, 'skills', name)
    
    if os.path.exists(dest):
        print(f'Error: Target already exists: {dest}')
        sys.exit(1)
    
    if not os.path.exists(src):
        print(f'Error: Source not found: {src}')
        sys.exit(1)
    
    skill_md = os.path.join(src, 'SKILL.md')
    if not os.path.exists(skill_md):
        print(f'Warning: Source does not contain SKILL.md. Not a valid skill?')
    
    try:
        shutil.copytree(src, dest)
    except Exception as e:
        print(f'Error copying files: {e}')
        sys.exit(1)
    
    if not run(['git', 'add', os.path.join('skills', name)], cwd=repo_root):
        sys.exit(1)
    
    if not run(['git', 'commit', '-m', f'Add skill {name} (copied)'], cwd=repo_root):
        print('Warning: Commit failed. Check git status.')
    
    print(f'Successfully copied {name} to skills/.')


def main():
    p = argparse.ArgumentParser(description='Add a skill to the collection')
    p.add_argument('--submodule', help='Git URL to add as submodule')
    p.add_argument('--copy', help='Local path to copy into skills/')
    p.add_argument('--name', required=True, help='Name for the skill directory')
    p.add_argument('--repo-root', 
                   default=os.path.expanduser('~/.my-skills-collection'),
                   help='Path to skills repository')
    p.add_argument('-y', '--yes', action='store_true',
                   help='Skip confirmation prompt')
    args = p.parse_args()
    
    if not (args.submodule or args.copy):
        p.error('Specify --submodule or --copy')
    
    if not os.path.exists(args.repo_root):
        print(f'Error: Repository not found: {args.repo_root}')
        sys.exit(1)
    
    if not is_git_repo(args.repo_root):
        print(f'Error: Not a git repository: {args.repo_root}')
        sys.exit(1)
    
    if not args.yes and not confirm(f'Add skill "{args.name}" to {args.repo_root}?'):
        print('Aborted.')
        return
    
    if args.submodule:
        add_submodule(args.submodule, args.name, args.repo_root)
    else:
        copy_skill(args.copy, args.name, args.repo_root)


if __name__ == '__main__':
    main()