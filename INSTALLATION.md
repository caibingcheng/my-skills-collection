## Structure

- `skills/`: Contains various global skills that can be used by AI agents.

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

For each skill is this repo's `skills/` directory,
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

### Note

- DO NOT hard link the entire `skills/` directory, only the individual skill directories inside it.
