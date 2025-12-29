# Git & GitHub Mastery: The Ultimate A-Z Curriculum

**Target Audience:** Zero to Hero
**Goal:** Deep internal understanding and operational mastery suitable for professional presentation.

---

## Phase 1: The Core Architecture
*Understanding the internal graph database before touching commands.*

### 1.1 The Distributed Model vs. Centralized
* **Concept:** Git is Distributed Version Control (DVCS). Every developer has a *full* copy of the repository history on their hard drive, not just the latest files. It uses SHA-1 hashing to ensure data integrity.
* **Difference with Perforce:** Perforce is Centralized (CVCS). The server holds the history; the user only holds the workspace. If the Perforce server goes down, you cannot version control. If GitHub goes down, you can still commit in Git.
* **Gotcha:** Don't treat Git like a backup folder. It is a history graph. Large binary files will bloat the local repo size for everyone forever (unlike Perforce).

### 1.2 The Three Trees (The Three States)
* **Concept:**
    1.  **Working Directory:** The sandbox where you edit files.
    2.  **Staging Area (Index):** A preparation zone where you assemble the next snapshot.
    3.  **Repository (HEAD):** The permanent database of committed snapshots.
* **Difference with Perforce:** Perforce uses "Changelists." Files are either "opened for edit" or not. Git adds the intermediate "Staging" layer, allowing you to curate commits precisely.
* **Gotcha:** Beginners often forget to `add` files to the Staging Area and wonder why `git commit` says "nothing to commit."

### 1.3 The HEAD Pointer
* **Concept:** `HEAD` is simply a pointer (a reference) that points to the branch you are currently on. It answers the question: "Where am I right now?"
* **Difference with Perforce:** Perforce relies on "Client Specs" to map views. Git relies on the `HEAD` pointer moving around the graph.
* **Gotcha:** Moving `HEAD` manually (via reset/checkout) changes what your files look like on disk instantly.

---

## Phase 2: Local Operations (The Daily Cycle)

### 2.1 Initialization & Configuration
* **Commands:** `git init`, `git config --global user.name`, `git config --global core.editor`
* **Concept:** Creating the `.git` folder (the database) and setting identity.
* **Difference with Perforce:** No server connection needed to start. Perforce requires an administrator to create a "Depot" and a user account first.
* **Gotcha:** forgetting to set `user.email` correctly causes your commits on GitHub to not link to your profile picture/account.

### 2.2 Staging & Committing (Snapshots)
* **Commands:** `git add .`, `git add -p`, `git commit -m`, `git commit --amend`
* **Concept:** A commit is not a diff; it is a full snapshot of the project at that moment. Git optimizes storage by referencing unchanged files from previous snapshots.
* **Difference with Perforce:** Perforce locks files (Checkout). Git does not lock files; it merges changes later.
* **Gotcha:** Using `git commit -m "update"` repeatedly. Commits should be atomic units of work with descriptive messages.

### 2.3 The .gitignore File
* **Commands:** (Editing `.gitignore`), `git rm --cached`
* **Concept:** Telling Git which files to intentionally untrack (logs, binaries, secrets, node_modules).
* **Difference with Perforce:** Perforce uses an "Ignore List" usually managed on the server or client spec. Git manages this via a file inside the repo itself.
* **Gotcha:** Adding a file to `.gitignore` *after* it has been tracked does nothing. You must untrack it first using `git rm --cached`.

---

## Phase 3: Branching & Navigation

### 3.1 Branching Mechanics
* **Commands:** `git branch`, `git switch -c <name>`, `git checkout -b`
* **Concept:** A branch in Git is incredibly lightweight—it is just a movable pointer to a specific commit hash. It costs almost 0 storage.
* **Difference with Perforce:** Perforce streams/branches are heavy directories (often requiring file copying on the server). Git branching is instantaneous.
* **Gotcha:** Deleting a branch `git branch -d` only deletes the *pointer*, not the commit history (unless those commits are unreachable/garbage collected).

### 3.2 Detached HEAD State
* **Commands:** `git checkout <commit-hash>`
* **Concept:** This happens when you check out a specific commit instead of a branch. `HEAD` is pointing directly to a commit, not a branch name. You are in "exploration mode."
* **Difference with Perforce:** Perforce allows "Time Lapse" views, but doesn't really have a workspace state where you aren't on a stream.
* **Gotcha:** If you make commits in Detached HEAD, they belong to no branch. If you switch away, those commits are "lost" (orphaned) and will eventually be deleted by Git's Garbage Collector.

### 3.3 Merging & Fast-Forward
* **Commands:** `git merge`, `git merge --no-ff`
* **Concept:** Combining two histories.
    * *Fast-Forward:* Just moving the pointer forward (linear).
    * *3-Way Merge:* Creating a new "Merge Commit" that ties two divergent histories together.
* **Difference with Perforce:** Perforce integration usually requires a central server calculation. Git merging happens locally using common ancestors.
* **Gotcha:** "Merge Conflicts." Don't panic. It just means Git needs human help to decide which lines to keep.

---

## Phase 4: Remote Repositories & Syncing

### 4.1 Remotes & Upstream
* **Commands:** `git remote add`, `git remote -v`, `git push -u origin main`
* **Concept:**
    * **Remote:** A shortcut name (usually `origin`) for a URL.
    * **Upstream:** The link between your *local* branch and a *remote* branch (e.g., local `main` tracks `origin/main`).
* **Difference with Perforce:** Perforce has one central depot. Git can theoretically have multiple remotes (e.g., one for production, one for your fork, one for a colleague).
* **Gotcha:** Getting "refused to merge unrelated histories" when trying to pull from a repo that was initialized separately.

### 4.2 Fetching vs. Pulling
* **Commands:** `git fetch`, `git pull`, `git pull --rebase`
* **Concept:**
    * `fetch`: Downloads data to your local database but touches nothing in your working directory.
    * `pull`: Runs `fetch` and immediately runs `merge`.
* **Difference with Perforce:** `p4 get` / `p4 sync` updates your files immediately. Git separates the "download" from the "update workspace" step (via fetch).
* **Gotcha:** Using `git pull` creates messy "Merge branch..." commits in your history. Prefer `git pull --rebase` for a cleaner linear history.

---

## Phase 5: Advanced History Manipulation (The "Danger Zone")

### 5.1 Rebasing
* **Commands:** `git rebase <branch>`, `git rebase -i` (Interactive)
* **Concept:** Re-writing history by lifting your commits and placing them on top of the latest code. Used to keep history linear.
* **Difference with Perforce:** You cannot rewrite history in Perforce. Once submitted, a changelist is immutable. Git allows you to curate history like an author edits a book.
* **Gotcha:** **The Golden Rule:** Never rebase a branch that creates shared history (i.e., don't rebase `main` or a branch others are working on). You will break their code.

### 5.2 Reset vs. Revert
* **Commands:** `git reset --hard`, `git reset --soft`, `git revert`
* **Concept:**
    * `reset`: Moves the HEAD pointer backward (rewrites history/erases commits).
    * `revert`: Creates a *new* commit that acts as the opposite of a previous commit (safe for shared history).
* **Difference with Perforce:** `p4 backout` is similar to `git revert`. `git reset` has no equivalent in Perforce because you can't locally delete submitted history in P4.
* **Gotcha:** `git reset --hard` is one of the few ways to permanently lose work in Git if you haven't committed it yet.

### 5.3 Stashing
* **Commands:** `git stash`, `git stash pop`, `git stash apply`
* **Concept:** A stack to temporarily store dirty changes so you can switch branches without committing half-finished work.
* **Difference with Perforce:** Similar to "Shelving" in Perforce.
* **Gotcha:** `git stash pop` removes the stash from the stack. If there is a conflict during the pop, it might get messy. Use `stash apply` to keep a copy just in case.

---

## Phase 6: Submodules & Large Files

### 6.1 Git Submodules
* **Commands:** `git submodule add <url>`, `git submodule update --init --recursive`
* **Concept:** Embedding one Git repository inside another. The parent repo only tracks the *Commit ID* of the child repo, not the files themselves.
* **Difference with Perforce:** Perforce uses "Workspace Mappings" to map different depot paths into one folder. Git uses Submodules, which are notoriously more complex to manage.
* **Gotcha:** Cloning a repo with submodules results in empty folders by default. You must run `git submodule update --init`. Also, forgetting to push changes in the submodule before pushing the parent repo breaks the build for everyone else.

### 6.2 Git LFS (Large File Storage)
* **Commands:** `git lfs track "*.psd"`
* **Concept:** Git is bad at binaries (images/videos). LFS replaces big files with text pointers inside Git, while storing the actual blob on a separate server.
* **Difference with Perforce:** Perforce handles gigabyte-sized binaries natively and efficiently. Git requires this add-on (LFS) to compete.
* **Gotcha:** If you commit a large file *before* installing LFS, it remains in your history forever, bloating the clone size, even if you delete it later.

---

## Phase 7: GitHub Workflow & Social Coding

### 7.1 Forking & Pull Requests (PRs)
* **Concept:**
    * **Fork:** A server-side clone of a repo to your account.
    * **PR:** A request to merge your fork's branch into the original repo's branch.
* **Difference with Perforce:** Perforce uses "Swarm" for reviews, but the concept of "Forking" (copying the whole depot) is rare. P4 development is usually on the same central server.
* **Gotcha:** Making changes to your `main` branch directly in your fork makes it hard to sync with the original repo later. Always use feature branches.

### 7.2 GitHub Actions (CI/CD)
* **Concept:** Automation pipelines defined in YAML files (testing, linting, deploying) triggered by Git events.
* **Difference with Perforce:** Perforce usually integrates with external tools like Jenkins. GitHub has this built natively into the platform.
* **Gotcha:** Infinite loops (an Action that pushes a commit, which triggers the Action again).

---

## Phase 8: Debugging & Repair

### 8.1 Bisect
* **Commands:** `git bisect start`, `git bisect good`, `git bisect bad`
* **Concept:** Using binary search to find exactly which commit introduced a bug.
* **Difference with Perforce:** `p4 timelapse` helps visually, but Git Bisect is an automated algorithmic approach.
* **Gotcha:** Only works well if your history is "buildable" (i.e., every commit actually compiles).

### 8.2 Reflog (The Safety Net)
* **Commands:** `git reflog`
* **Concept:** A local log of everywhere HEAD has been. It allows you to recover "lost" commits (e.g., after a bad reset or rebase).
* **Difference with Perforce:** Perforce keeps everything forever on the server. Reflog is your local "Undoing the Undo" mechanism.
* **Gotcha:** The Reflog is local only and temporary (expires after 90 days usually). It won't help you recover a deleted branch on someone else's machine.