#!/usr/bin/env python3
"""
Git sync script with automatic commit message generation and email verification.

This script automates the git sync workflow:
1. Checks email consistency with recent commits
2. Generates commit message matching historical patterns
3. Commits and pushes changes
"""

import subprocess
import sys
import os
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from analyze_commits import get_recent_commits, analyze_message_patterns
from check_email import get_recent_commit_emails, get_current_git_email, check_email_consistency


def run_git_command(args: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command and return the result."""
    return subprocess.run(
        ['git'] + args,
        capture_output=True,
        text=True,
        check=check
    )


def has_changes() -> bool:
    """Check if there are uncommitted changes."""
    result = run_git_command(['status', '--porcelain'], check=False)
    return bool(result.stdout.strip())


def get_staged_changes() -> str:
    """Get a summary of staged changes."""
    result = run_git_command(['diff', '--cached', '--stat'], check=False)
    return result.stdout


def get_unstaged_files() -> list:
    """Get list of unstaged/modified files."""
    result = run_git_command(['status', '--porcelain'], check=False)
    files = []
    for line in result.stdout.strip().split('\n'):
        if line:
            # Format: XY filename or XY "filename with spaces"
            status = line[:2]
            filename = line[3:].strip('"')
            files.append((status, filename))
    return files


def categorize_changes(files: list) -> dict:
    """Categorize changes by type."""
    categories = {
        'added': [],
        'modified': [],
        'deleted': [],
        'renamed': []
    }

    for status, filename in files:
        if status in ['A ', 'AM']:
            categories['added'].append(filename)
        elif status in ['M ', 'MM']:
            categories['modified'].append(filename)
        elif status in ['D ']:
            categories['deleted'].append(filename)
        elif status in ['R ']:
            categories['renamed'].append(filename)
        elif status[1] in ['M', 'A', 'D']:
            # Staged changes
            if status[1] == 'M':
                categories['modified'].append(filename)
            elif status[1] == 'A':
                categories['added'].append(filename)
            elif status[1] == 'D':
                categories['deleted'].append(filename)

    return categories


def generate_commit_message(patterns: dict, categories: dict, custom_msg: str = None) -> str:
    """
    Generate a commit message based on historical patterns.

    Args:
        patterns: Analysis of historical commit patterns
        categories: Dictionary of change categories
        custom_msg: Optional custom message base

    Returns:
        Generated commit message string
    """
    if custom_msg:
        base_msg = custom_msg
    else:
        # Determine the primary action based on changes
        if categories['added'] and not categories['modified'] and not categories['deleted']:
            verb = 'Add'
            what = categorize_file_types(categories['added'])
        elif categories['deleted'] and not categories['added'] and not categories['modified']:
            verb = 'Remove'
            what = categorize_file_types(categories['deleted'])
        elif categories['modified'] and not categories['added'] and not categories['deleted']:
            verb = 'Update'
            what = categorize_file_types(categories['modified'])
        else:
            # Mixed changes
            verb = 'Update'
            what = 'files'

        base_msg = f"{verb} {what}"

    # Apply formatting based on patterns
    if not patterns.get('capitalization', {}).get('uses_capital', True):
        base_msg = base_msg[0].lower() + base_msg[1:]
    else:
        base_msg = base_msg[0].upper() + base_msg[1:]

    if patterns.get('punctuation', {}).get('uses_period', False):
        base_msg += '.'

    return base_msg


def categorize_file_types(files: list) -> str:
    """Categorize files into descriptive groups."""
    if not files:
        return 'files'

    if len(files) == 1:
        return files[0]

    # Check for common patterns
    extensions = set()
    for f in files:
        ext = os.path.splitext(f)[1]
        if ext:
            extensions.add(ext)

    # Check if all files are in a specific directory
    dirs = set(os.path.dirname(f).split('/')[0] for f in files if os.path.dirname(f))

    if len(files) == 1:
        return files[0]
    elif len(dirs) == 1 and dirs:
        dir_name = dirs.pop()
        if dir_name:
            return f'{len(files)} files in {dir_name}/'
    elif len(extensions) == 1:
        ext = extensions.pop()
        return f'{len(files)} {ext} files'
    else:
        return f'{len(files)} files'


def stage_all_changes():
    """Stage all changes including new files."""
    run_git_command(['add', '-A'])


def commit_changes(message: str) -> bool:
    """Commit staged changes with the given message."""
    try:
        run_git_command(['commit', '-m', message])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error committing: {e.stderr}", file=sys.stderr)
        return False


def push_changes(branch: str = None) -> bool:
    """Push changes to remote."""
    try:
        if branch:
            run_git_command(['push', 'origin', branch])
        else:
            run_git_command(['push'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pushing: {e.stderr}", file=sys.stderr)
        return False


def get_current_branch() -> str:
    """Get the current git branch name."""
    try:
        result = run_git_command(['branch', '--show-current'])
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Sync git changes with automatic commit message generation'
    )
    parser.add_argument(
        '-m', '--message',
        help='Custom commit message (optional, will auto-generate if not provided)'
    )
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='Commit only, do not push'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Skip email verification'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--email-count',
        type=int,
        default=5,
        help='Number of commits to check for email consistency (default: 5)'
    )
    parser.add_argument(
        '--pattern-count',
        type=int,
        default=5,
        help='Number of commits to analyze for message patterns (default: 5)'
    )

    args = parser.parse_args()

    # Check if we're in a git repository
    if run_git_command(['rev-parse', '--git-dir'], check=False).returncode != 0:
        print("❌ Not in a git repository", file=sys.stderr)
        return 1

    # Check for changes
    if not has_changes():
        print("✓ No changes to commit")
        return 0

    # Step 1: Email verification
    if not args.force:
        print("📧 Checking email consistency...")
        commits = get_recent_commit_emails(args.email_count)
        current_email = get_current_git_email()
        is_valid, message = check_email_consistency(commits, current_email)

        if not is_valid:
            print(message)
            print("\nTo continue anyway, run with --force flag")
            return 1
        else:
            print(f"  {message}")

    # Step 2: Analyze commit patterns
    print("\n📊 Analyzing commit message patterns...")
    commits = get_recent_commits(args.pattern_count)
    patterns = analyze_message_patterns(commits)

    # Get change categories
    files = get_unstaged_files()
    categories = categorize_changes(files)

    # Generate commit message
    commit_msg = generate_commit_message(patterns, categories, args.message)

    print(f"  Pattern: {'conventional commits' if patterns.get('conventional_commits', {}).get('uses') else 'simple messages'}")
    print(f"  Capitalization: {'first letter uppercase' if patterns.get('capitalization', {}).get('uses_capital') else 'first letter lowercase'}")

    # Show what will be committed
    print("\n📝 Changes to be committed:")
    for status, filename in files:
        print(f"  {status} {filename}")

    print(f"\n💬 Generated commit message: \"{commit_msg}\"")

    if args.dry_run:
        print("\n⏹️  Dry run - no changes made")
        return 0

    # Step 3: Stage and commit
    print("\n📦 Staging changes...")
    stage_all_changes()

    print(f"🚀 Committing...")
    if not commit_changes(commit_msg):
        return 1

    print(f"  ✓ Committed: {commit_msg}")

    # Step 4: Push
    if not args.no_push:
        branch = get_current_branch()
        print(f"\n☁️  Pushing to {branch}...")
        if push_changes():
            print(f"  ✓ Pushed to origin/{branch}")
        else:
            return 1
    else:
        print("\n⏭️  Skipping push (--no-push)")

    print("\n✅ Sync complete!")
    return 0


if __name__ == '__main__':
    exit(main())
