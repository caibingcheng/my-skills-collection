#!/usr/bin/env python3
"""
Analyze git commit history to extract message format patterns.

This script analyzes the last N commits to understand:
1. Message style (imperative vs descriptive)
2. Common prefixes (feat:, fix:, etc.)
3. Average length and structure
4. Common verbs and patterns
"""

import subprocess
import re
from collections import Counter
from typing import List, Dict, Any


def get_recent_commits(count: int = 5) -> List[Dict[str, str]]:
    """Get recent commits with their messages and authors."""
    try:
        result = subprocess.run(
            ['git', 'log', f'-n{count}', '--format=%H|%s|%an|%ae'],
            capture_output=True,
            text=True,
            check=True
        )

        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0][:7],
                        'message': parts[1],
                        'author': parts[2],
                        'email': parts[3]
                    })
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error getting commits: {e}")
        return []


def analyze_message_patterns(commits: List[Dict[str, str]]) -> Dict[str, Any]:
    """Analyze commit message patterns."""
    messages = [c['message'] for c in commits]

    if not messages:
        return {}

    # Check for conventional commits pattern (type: message)
    conventional_pattern = re.compile(r'^(\w+)(\(.+\))?!?:\s*(.+)$')
    conventional_count = sum(1 for m in messages if conventional_pattern.match(m))

    # Extract first words (verbs)
    first_words = []
    for msg in messages:
        # Skip prefixes like "feat:", "fix:"
        clean_msg = re.sub(r'^\w+(\(.+\))?!?:\s*', '', msg)
        words = clean_msg.split()
        if words:
            first_word = words[0].lower()
            # Remove trailing punctuation
            first_word = re.sub(r'[^\w]$', '', first_word)
            first_words.append(first_word)

    word_counter = Counter(first_words)

    # Check capitalization patterns
    capitalized = sum(1 for m in messages if m and m[0].isupper())

    # Check for period at end
    with_period = sum(1 for m in messages if m.endswith('.'))

    # Average length
    avg_length = sum(len(m) for m in messages) / len(messages)

    # Common verbs in commit messages
    common_verbs = ['add', 'update', 'fix', 'remove', 'implement', 'refactor',
                    'create', 'delete', 'modify', 'change', 'improve', 'optimize']
    verb_usage = {verb: word_counter.get(verb, 0) for verb in common_verbs}

    return {
        'conventional_commits': {
            'uses': conventional_count > len(messages) / 2,
            'percentage': (conventional_count / len(messages) * 100) if messages else 0
        },
        'capitalization': {
            'uses_capital': capitalized > len(messages) / 2,
            'percentage': (capitalized / len(messages) * 100) if messages else 0
        },
        'punctuation': {
            'uses_period': with_period > len(messages) / 2,
            'percentage': (with_period / len(messages) * 100) if messages else 0
        },
        'average_length': round(avg_length, 1),
        'common_first_words': word_counter.most_common(5),
        'verb_usage': {k: v for k, v in verb_usage.items() if v > 0},
        'sample_messages': messages[:3]
    }


def get_format_summary(patterns: Dict[str, Any]) -> str:
    """Generate a human-readable format summary."""
    lines = []

    if patterns.get('conventional_commits', {}).get('uses'):
        lines.append("Uses conventional commits (e.g., 'feat:', 'fix:')")
    else:
        lines.append("Uses simple commit messages (no conventional commit prefixes)")

    cap = patterns.get('capitalization', {})
    if cap.get('uses_capital'):
        lines.append("Messages start with capital letter")
    else:
        lines.append("Messages start with lowercase letter")

    punct = patterns.get('punctuation', {})
    if punct.get('uses_period'):
        lines.append("Messages end with period")
    else:
        lines.append("Messages don't end with period")

    avg_len = patterns.get('average_length', 0)
    lines.append(f"Average message length: {avg_len} characters")

    common_words = patterns.get('common_first_words', [])
    if common_words:
        words_str = ', '.join([f"{w}({c})" for w, c in common_words[:3]])
        lines.append(f"Common first words: {words_str}")

    return '\n'.join(lines)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze git commit message patterns'
    )
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=5,
        help='Number of commits to analyze (default: 5)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    commits = get_recent_commits(args.count)
    if not commits:
        print("No commits found or not in a git repository")
        return 1

    patterns = analyze_message_patterns(commits)

    if args.json:
        import json
        print(json.dumps(patterns, indent=2))
    else:
        print("Commit Message Pattern Analysis")
        print("=" * 40)
        print()
        print(get_format_summary(patterns))
        print()
        print("Recent commits analyzed:")
        for c in commits:
            print(f"  {c['hash']} - {c['message'][:60]}")

    return 0


if __name__ == '__main__':
    exit(main())
