#!/usr/bin/env bash
# 检查 skills 目录下是否存在循环符号链接
# 循环链接定义：符号链接指向其父目录

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

found=0

if [ -d "$SKILLS_DIR" ]; then
    while IFS= read -r -d '' link; do
        target=$(readlink -f "$link")
        parent_dir=$(dirname "$link")
        parent_real=$(readlink -f "$parent_dir")
        
        if [ "$target" = "$parent_real" ]; then
            echo "ERROR: Circular symlink detected: $link -> $target"
            found=1
        fi
    done < <(find "$SKILLS_DIR" -type l -print0)
fi

if [ $found -eq 1 ]; then
    echo ""
    echo "Found circular symlinks. Please remove them before committing."
    exit 1
fi

exit 0