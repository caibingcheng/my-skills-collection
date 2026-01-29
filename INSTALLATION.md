## Structure

- `skills/`: Contains various skills that can be used by AI agents.

## Skills Installation

Clone the repository to a regular location on your system, for example:

```bash
git clone https://github.com/caibingcheng/my-skills-collection.git ~/projects/my-skills-collection
```

For each skill is this repo's `skills/` directory,
hard link it to the `skills/` directory from your AI agent's skills directory.

Note: DO NOT hard link the entire `skills/` directory, only the individual skill directories inside it.

Different AI agents may have different skills directories. Here are some examples:

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
