#!/usr/bin/env bash
# 初始化 git hooks

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Initializing git hooks..."

mkdir -p "$HOOKS_DIR"

ln -sf ../../scripts/check-circular-links.sh "$HOOKS_DIR/pre-commit"

echo "✓ pre-commit hook installed (checks circular symlinks)"