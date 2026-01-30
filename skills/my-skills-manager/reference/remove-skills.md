## Instruction

Steps to remove skills from my-skills-collection repository.

## Steps

1. Determine the skill you want to remove from `skills/` directory in my-skills-collection repository.
2. Ask to confirm the removal of the skill.
3. If the skill is added as a submodule, remove the submodule:
    ```bash
    cd ~/.my-skills-collection
    git submodule deinit -f skills/<skill-name>
    rm -rf .git/modules/skills/<skill-name>
    git rm -f skills/<skill-name>
    git commit -m "Remove skill <skill-name> submodule"
    ```
4. If the skill is just copied, remove the skill directory and commit the changes:
    ```bash
    cd ~/.my-skills-collection
    rm -rf skills/<skill-name>
    git add -u skills/<skill-name>
    git commit -m "Remove skill <skill-name>"
    ```
    Make sure to replace `<skill-name>` with the actual name of the skill you want to remove.
