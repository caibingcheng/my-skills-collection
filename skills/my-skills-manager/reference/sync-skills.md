## Instruction

Steps to sync skills in my-skills-collection repository.

## Steps

1. Commit current changes in the my-skills-collection repository to avoid conflicts:

   ```bash
   cd ~/.my-skills-collection
   git add .
   git commit -m "Save current changes before syncing"
   ```
2. Sync the entire my-skills-collection repository:

   ```bash
   cd ~/.my-skills-collection
   git pull origin main
   git submodule update --remote --merge
   ```
3. After syncing, review the changes and resolve any merge conflicts if they arise.
4. Rebase or merge as necessary to integrate the latest changes.
5. Push the updated local repository back to the remote if you have made any changes:

   ```bash
   git push origin main
   ```
