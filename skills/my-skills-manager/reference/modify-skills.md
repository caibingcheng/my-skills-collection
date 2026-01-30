## Instruction

Steps to modify skills to my-skills-collection repository.

## Steps

1. Determine the skill you want to modify in `skills/` directory in my-skills-collection repository.
2. Make the necessary changes to the skill files.
3. After making changes, commit the modifications:
    ```bash
    cd ~/.my-skills-collection
    git add skills/<skill-name>
    git commit -m "Modify skill <skill-name>"
    ```
    Make sure to replace `<skill-name>` with the actual name of the skill you modified.
4. If the skill is a submodule and you need to update it to a newer version, navigate to the submodule directory and pull the latest changes:
    ```bash
    cd ~/.my-skills-collection/skills/<skill-name>
    git pull origin main
    cd ~/.my-skills-collection
    git add skills/<skill-name>
    git commit -m "Update submodule skill <skill-name> to latest version"
    ```
5. Push the updated local repository back to the remote:
    ```bash
    git push origin main
    ```
    This ensures that your modifications are reflected in the remote repository.
