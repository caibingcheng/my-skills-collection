#!/usr/bin/env python3
"""List all valid skills in ~/.my-skills-collection.

A valid skill is a directory containing a SKILL.md file.

Usage:
  python list_skills.py [--repo-root PATH]
"""
import argparse
import os
import sys


def get_skill_info(skill_dir):
    """Extract name and description from SKILL.md if available."""
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_md):
        return None
    
    name = os.path.basename(skill_dir)
    description = ''
    
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            # Try to extract description from YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.strip().split('\n'):
                        if line.startswith('description:'):
                            description = line.split(':', 1)[1].strip()
                            break
    except Exception:
        pass
    
    return {'name': name, 'description': description, 'path': skill_dir}


def list_skills(repo_root):
    """List all valid skills in the repository."""
    skills_dir = os.path.join(repo_root, 'skills')
    
    if not os.path.exists(repo_root):
        print(f'Error: Repository not found: {repo_root}')
        sys.exit(1)
    
    if not os.path.exists(skills_dir):
        print(f'Error: Skills directory not found: {skills_dir}')
        sys.exit(1)
    
    skills = []
    for entry in os.listdir(skills_dir):
        skill_dir = os.path.join(skills_dir, entry)
        if os.path.isdir(skill_dir):
            info = get_skill_info(skill_dir)
            if info:
                skills.append(info)
    
    return skills


def main():
    p = argparse.ArgumentParser(description='List installed skills')
    p.add_argument('--repo-root', 
                   default=os.path.expanduser('~/.my-skills-collection'),
                   help='Path to skills repository')
    p.add_argument('--json', action='store_true',
                   help='Output as JSON')
    args = p.parse_args()
    
    skills = list_skills(args.repo_root)
    
    if not skills:
        print('No skills found.')
        return
    
    if args.json:
        import json
        print(json.dumps(skills, indent=2))
    else:
        print(f'Found {len(skills)} skill(s) in {args.repo_root}/skills/:\n')
        for skill in sorted(skills, key=lambda s: s['name']):
            desc = skill['description'][:60] + '...' if len(skill['description']) > 60 else skill['description']
            print(f"  {skill['name']}")
            if desc:
                print(f"    {desc}")
            print()


if __name__ == '__main__':
    main()