## Instruction

Steps to add skills to my-skills-collection repository.

## Steps

1. Determine you want to add a submodule or just copy the skill files.
2. As default, skills are added to `skills/` directory in my-skills-collection repository, unless the installed directory is specified.
3. If you want to add a submodule, add the submodule to my-skills-collection repository:

   ```bash
   cd ~/.my-skills-collection
   git submodule add <skill-repo-url> skills/<skill-name>
   git commit -m "Add skill <skill-name> as submodule"
   ```

4. If you want to just copy the skill files, copy the skill directory to `skills/` directory and commit the changes:

   ```bash
   cp -r <path-to-skill> ~/.my-skills-collection/skills/<skill-name>
   cd ~/.my-skills-collection
   git add skills/<skill-name>
   git commit -m "Add skill <skill-name>"
   ```

   If the skill is a url, you need to download it and then copy it to the `skills/` directory.

   As better practice, add the download url to .skill-metadata.json file in the skill directory if applicable.
