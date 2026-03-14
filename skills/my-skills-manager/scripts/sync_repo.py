#!/usr/bin/env python3
"""Sync the my-skills-collection repository and update submodules.

Usage:
  python sync_repo.py [--repo-root PATH]
"""
import argparse
import os
import subprocess
import sys


def run(cmd, cwd=None, check=True):
    """Run a command and return result."""
    print('>>>', ' '.join(cmd))
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f'Error: {result.stderr.strip()}')
        return None
    return result


def get_current_branch(repo_root):
    """Get the current git branch name."""
    result = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_root, check=False)
    if result and result.returncode == 0:
        return result.stdout.strip()
    return None


def has_changes(repo_root):
    """Check if there are uncommitted changes."""
    result = run(['git', 'status', '--porcelain'], cwd=repo_root, check=False)
    return result and result.stdout.strip() != ''


def main():
    p = argparse.ArgumentParser(description='Sync skills repository')
    p.add_argument('--repo-root', 
                   default=os.path.expanduser('~/.my-skills-collection'),
                   help='Path to skills repository')
    args = p.parse_args()
    
    repo_root = os.path.expanduser(args.repo_root)
    
    if not os.path.exists(repo_root):
        print(f'Error: Repository not found: {repo_root}')
        print('Clone it first:')
        print('  git clone https://github.com/caibingcheng/my-skills-collection.git ~/.my-skills-collection')
        sys.exit(1)
    
    branch = get_current_branch(repo_root)
    if not branch:
        print('Error: Not a git repository or detached HEAD')
        sys.exit(1)
    
    print(f'Repository: {repo_root}')
    print(f'Branch: {branch}')
    print()
    
    # Commit any local changes
    if has_changes(repo_root):
        print('Saving local changes...')
        run(['git', 'add', '.'], cwd=repo_root)
        result = run(['git', 'commit', '-m', 'Save changes before sync'], 
                     cwd=repo_root, check=False)
        if not result or result.returncode != 0:
            print('No changes to commit or commit failed.')
    
    # Pull from remote
    print(f'\nPulling from origin/{branch}...')
    result = run(['git', 'pull', 'origin', branch], cwd=repo_root, check=False)
    if not result or result.returncode != 0:
        # Try alternative branch names
        for alt_branch in ['main', 'master']:
            if alt_branch != branch:
                print(f'Trying origin/{alt_branch}...')
                result = run(['git', 'pull', 'origin', alt_branch], cwd=repo_root, check=False)
                if result and result.returncode == 0:
                    break
        else:
            print('Warning: Pull failed. Check your connection or resolve conflicts.')
    
    # Update submodules
    print('\nUpdating submodules...')
    result = run(['git', 'submodule', 'update', '--remote', '--merge'], 
                 cwd=repo_root, check=False)
    if result and result.returncode == 0:
        print('Submodules updated.')
    else:
        print('Warning: Submodule update had issues.')
    
    print('\n✓ Sync complete.')
    print('Review changes and run "git push" if needed.')


if __name__ == '__main__':
    main()