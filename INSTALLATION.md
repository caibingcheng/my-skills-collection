## Structure

- `skills/`: Contains various global skills that can be used by AI agents.

Each skill is organized in its own directory under `skills/` or some other specified directory, with a `SKILL.md` file that describes the skill's name, description, and usage instructions.
If a folder under `skills/` or some other specified directory does not contain a `SKILL.md` file, it will be ignored as a skill.

For example,

```
skills/
├── task-verification/
│   └── SKILL.md
├── code-refactoring/
│   └── SKILL.md
├── data-analysis/
│   └── SKILL.md
└── some-other-folder/ # No SKILL.md inside
```

`task-verification/`, `code-refactoring/`, and `data-analysis/` are valid skills because they contain `SKILL.md` files, while `some-other-folder/` is not a valid skill and will be ignored.


## Skills Installation

Clone the repository to a regular location on your system, for example:

```bash
git clone https://github.com/caibingcheng/my-skills-collection.git ~/.my-skills-collection
```

Or update an existing local clone:

```bash
cd ~/.my-skills-collection
git pull origin master
```

For each skill in this repo's `skills/` directory,
hard link it to the `skills/` directory from your AI agent's skills directory.

Different AI agents may have different skills directories.
Install skills to global directories as default, or to project-specific directories if specified.

Here are some examples:

- OpenCode:
  - global: `~/.config/opencode/skills`
  - project: `.opencode/skills/`
- VSCode:
  - global: `~/.copilot/skills/`
  - project: `.github/skills/`
- Github Copilot:
  - global: `~/.copilot/skills/`
  - project: `.github/skills/`

If the `skills/` directory does not exist, create it first.

## Git Hooks Setup (Recommended)

After cloning, run the init script to set up git hooks:

```bash
~/.my-skills-collection/scripts/init-hooks.sh
```

This will install a pre-commit hook that prevents circular symlinks from being committed.

### Note

- DO NOT hard link the entire `skills/` directory, only the individual skill directories inside it.
