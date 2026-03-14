## Installation Reference

How to install skills from `~/.my-skills-collection` to AI agents.

---

## Repository Structure

```
~/.my-skills-collection/
├── skills/
│   ├── my-skill/
│   │   └── SKILL.md
│   └── another-skill/
│       └── SKILL.md
└── README.md
```

Each skill is a directory containing a `SKILL.md` file. Directories without `SKILL.md` are ignored.

---

## Installation Methods

### Clone the Repository

```bash
git clone https://github.com/caibingcheng/my-skills-collection.git ~/.my-skills-collection
```

### Update Existing Clone

```bash
cd ~/.my-skills-collection
git pull origin master
```

---

## Installing to AI Agents

Use hard links to install individual skills to your AI agent's skills directory.

### Agent Skills Directories

| Agent | Global | Project |
|-------|--------|---------|
| OpenCode | `~/.config/opencode/skills` | `.opencode/skills/` |
| VSCode Copilot | `~/.copilot/skills/` | `.github/skills/` |

### Installation Example (OpenCode)

```bash
# Create directory if needed
mkdir -p ~/.config/opencode/skills

# Hard link individual skill (NOT the entire skills/ directory!)
ln ~/.my-skills-collection/skills/my-skill/SKILL.md ~/.config/opencode/skills/my-skill/
```

**Important**: Link individual skill directories, not the parent `skills/` directory.

---

## Why Hard Links?

- Changes in `~/.my-skills-collection` are immediately available to agents
- No need to copy files after updates
- Single source of truth for each skill