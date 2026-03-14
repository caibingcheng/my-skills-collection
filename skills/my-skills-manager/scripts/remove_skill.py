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


def run(cmd, cwd=None):
    """Run a command and return True if successful."""
    print('>>>', ' '.join(cmd))
    try:
        subprocess.check_call(cmd, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f'Error: Command failed with exit code {e.returncode}')
        return False


def is_submodule(name, repo_root):
    """Check if a skill is a git submodule."""
    gitmodules = os.path.join(repo_root, '.gitmodules')
    if os.path.exists(gitmodules):
        with open(gitmodules, 'r') as f:
            return name in f.read()
    return False


def confirm(prompt):
    """Ask for user confirmation."""
    try:
        resp = input(prompt + ' [y/N]: ').strip().lower()
        return resp == 'y'
    except EOFError:
        return False


def remove_submodule(name, repo_root):
    """Remove a submodule skill."""
    path = os.path.join('skills', name)
    
    print(f'Removing submodule: {name}')
    
    steps = [
        (['git', 'submodule', 'deinit', '-f', path], 'deinit'),
        (['rm', '-rf', os.path.join('.git', 'modules', 'skills', name)], 'remove git modules'),
        (['git', 'rm', '-f', path], 'git rm'),
    ]
    
    for cmd, desc in steps:
        if not run(cmd, cwd=repo_root):
            print(f'Warning: Failed to {desc}')
    
    if not run(['git', 'commit', '-m', f'Remove skill {name} submodule'], cwd=repo_root):
        print('Warning: Commit failed. Check git status.')
    
    print(f'Successfully removed submodule: {name}')


def remove_copied(name, repo_root):
    """Remove a copied (non-submodule) skill."""
    target = os.path.join(repo_root, 'skills', name)
    
    if not os.path.exists(target):
        print(f'Error: Skill not found: {target}')
        sys.exit(1)
    
    try:
        shutil.rmtree(target)
    except Exception as e:
        print(f'Error removing directory: {e}')
        sys.exit(1)
    
    if not run(['git', 'add', '-u', os.path.join('skills', name)], cwd=repo_root):
        print('Warning: git add failed')
    
    if not run(['git', 'commit', '-m', f'Remove skill {name}'], cwd=repo_root):
        print('Warning: Commit failed. Check git status.')
    
    print(f'Successfully removed: {name}')


def main():
    p = argparse.ArgumentParser(description='Remove a skill from the collection')
    p.add_argument('--name', required=True, help='Name of skill to remove')
    p.add_argument('--repo-root', 
                   default=os.path.expanduser('~/.my-skills-collection'),
                   help='Path to skills repository')
    p.add_argument('-y', '--yes', action='store_true',
                   help='Skip confirmation prompt')
    args = p.parse_args()
    
    if not os.path.exists(args.repo_root):
        print(f'Error: Repository not found: {args.repo_root}')
        sys.exit(1)
    
    target = os.path.join(args.repo_root, 'skills', args.name)
    if not os.path.exists(target):
        print(f'Error: Skill not found: {args.name}')
        print(f'  Expected: {target}')
        sys.exit(1)
    
    skill_type = 'submodule' if is_submodule(args.name, args.repo_root) else 'directory'
    
    if not args.yes and not confirm(f'Remove skill "{args.name}" ({skill_type})?'):
        print('Aborted.')
        return
    
    if skill_type == 'submodule':
        remove_submodule(args.name, args.repo_root)
    else:
        remove_copied(args.name, args.repo_root)


if __name__ == '__main__':
    main()