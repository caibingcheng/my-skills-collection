#!/usr/bin/env python3
"""
Check email consistency between recent commits and current git config.

This script:
1. Extracts emails from the last N commits
2. Checks if they all share the same domain
3. Compares with the current git user.email config
4. Returns appropriate exit codes and messages
"""

import subprocess
import re
import sys
from typing import List, Dict, Set, Tuple


def get_recent_commit_emails(count: int = 5) -> List[Dict[str, str]]:
    """Get emails from recent commits."""
    try:
        result = subprocess.run(
            ['git', 'log', f'-n{count}', '--format=%H|%an|%ae'],
            capture_output=True,
            text=True,
            check=True
        )

        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commits.append({
                        'hash': parts[0][:7],
                        'author': parts[1],
                        'email': parts[2]
                    })
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error getting commits: {e}", file=sys.stderr)
        return []


def get_current_git_email() -> str:
    """Get the currently configured git user email."""
    try:
        result = subprocess.run(
            ['git', 'config', 'user.email'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    match = re.search(r'@(.+)$', email)
    return match.group(1) if match else ""


def check_email_consistency(commits: List[Dict[str, str]], current_email: str) -> Tuple[bool, str]:
    """
    Check if emails are consistent.

    Returns:
        (is_valid, message): is_valid is True if checks pass, False otherwise
    """
    if not commits:
        return False, "No commits found to analyze"

    if not current_email:
        return False, "No git user.email configured. Run: git config user.email 'your@email.com'"

    # Extract domains from commit emails
    commit_domains = set()
    for commit in commits:
        domain = extract_domain(commit['email'])
        if domain:
            commit_domains.add(domain)

    if not commit_domains:
        return False, "Could not extract domains from commit emails"

    current_domain = extract_domain(current_email)

    # Check if all commits use the same domain
    if len(commit_domains) == 1:
        # All commits have the same domain
        commit_domain = commit_domains.pop()

        if current_domain != commit_domain:
            return False, (
                f"⚠️  Email domain mismatch detected!\n\n"
                f"Recent commits use: @{commit_domain}\n"
                f"Your config uses: @{current_domain}\n\n"
                f"To fix, run:\n"
                f"  git config user.email 'your.name@{commit_domain}'\n\n"
                f"Or if this is intentional, use --force to continue anyway."
            )
        else:
            return True, f"✓ Email consistency check passed. Domain: @{current_domain}"
    else:
        # Commits have different domains - let user decide
        domains_str = ', '.join(sorted(commit_domains))
        return False, (
            f"⚠️  Recent commits have inconsistent email domains: {domains_str}\n\n"
            f"Your current config: {current_email}\n\n"
            f"Please verify this is correct before continuing, "
            f"or use --force to skip this check."
        )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Check email consistency between commits and git config'
    )
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=5,
        help='Number of commits to check (default: 5)'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Skip email check and continue anyway'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    if args.force:
        if args.json:
            import json
            print(json.dumps({'valid': True, 'skipped': True}))
        else:
            print("⚡ Email check skipped (--force)")
        return 0

    commits = get_recent_commit_emails(args.count)
    current_email = get_current_git_email()

    is_valid, message = check_email_consistency(commits, current_email)

    if args.json:
        import json
        result = {
            'valid': is_valid,
            'current_email': current_email,
            'commit_count': len(commits),
            'commit_domains': list(set(extract_domain(c['email']) for c in commits if c['email'])),
            'message': message
        }
        print(json.dumps(result, indent=2))
    else:
        print(message)

    return 0 if is_valid else 1


if __name__ == '__main__':
    exit(main())
