## Operations Reference

Detailed procedures for managing skills in `~/.my-skills-collection`.

---

## Adding Skills

Skills can be added as git submodules (recommended for external repos) or copied directly.

### As Submodule (Recommended)

```bash
cd ~/.my-skills-collection
git submodule add <skill-repo-url> skills/<skill-name>
git commit -m "Add skill <skill-name> as submodule"
```

**Benefits**: Easy updates via `git submodule update --remote`

### By Copying

```bash
cp -r <path-to-skill> ~/.my-skills-collection/skills/<skill-name>
cd ~/.my-skills-collection
git add skills/<skill-name>
git commit -m "Add skill <skill-name>"
```

**Tip**: If downloading from a URL, save the source URL to `.skill-metadata.json` in the skill directory.

---

## Removing Skills

### Submodule

```bash
cd ~/.my-skills-collection
git submodule deinit -f skills/<skill-name>
rm -rf .git/modules/skills/<skill-name>
git rm -f skills/<skill-name>
git commit -m "Remove skill <skill-name> submodule"
```

### Copied Directory

```bash
cd ~/.my-skills-collection
rm -rf skills/<skill-name>
git add -u skills/<skill-name>
git commit -m "Remove skill <skill-name>"
```

---

## Modifying Skills

### For Copied Skills

```bash
# Edit files in skills/<skill-name>
cd ~/.my-skills-collection
git add skills/<skill-name>
git commit -m "Modify skill <skill-name>"
```

### For Submodule Skills

```bash
cd ~/.my-skills-collection/skills/<skill-name>
git pull origin main
cd ~/.my-skills-collection
git add skills/<skill-name>
git commit -m "Update submodule skill <skill-name>"
```

---

## Syncing Repository

Sync pulls latest changes and updates all submodules.

```bash
cd ~/.my-skills-collection

# 1. Save local changes
git add .
git commit -m "Save changes before sync"

# 2. Pull from remote (try main, then master)
git pull origin main || git pull origin master

# 3. Update all submodules
git submodule update --remote --merge

# 4. Resolve conflicts if any, then push
git push origin main
```

---

## Valid Skill Structure

A valid skill must contain a `SKILL.md` file:

```
skills/
├── my-skill/
│   └── SKILL.md        # Required
├── another-skill/
│   ├── SKILL.md
│   └── scripts/        # Optional
└── not-a-skill/        # Ignored - no SKILL.md
```

The `SKILL.md` must have YAML frontmatter with `name` and `description`.