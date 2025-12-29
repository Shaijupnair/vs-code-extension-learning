### Topic Core Operations
Here is the deep dive into **Phase 2: Core Operations**. This is your daily driver manual.

Since you are coming from Perforce, the most important thing to remember is that **Network operations are separate from File operations.** In Perforce, "Submit" does everything. In Git, saving your work and sharing your work are two different steps.

---

### 1. How to "Check In" Code

In Perforce, you add files to a Changelist and Submit.
In Git, this is a **Two-Stage Process**. You must first "Stage" the file (put it in the box), and then "Commit" it (seal the box).

#### The Process

1. **Modify:** You edit `extension.ts`. Git sees it is modified but won't save it yet.
2. **Stage (`git add`):** You tell Git, "I want this specific change to be part of the next snapshot."
3. **Commit (`git commit`):** You save the snapshot to your **Local** history.

#### Example Scenario

You created a new file `debugger.ts` and modified `package.json`.

```bash
# 1. Check status (See what changed)
git status
# Output:
# Untracked files: debugger.ts
# Modified: package.json

# 2. Stage the files (Prepare the snapshot)
git add debugger.ts package.json
# OR to add everything in the folder:
git add .

# 3. Commit (Save to Local History)
git commit -m "Added new debugger logic and updated version"

```

#### ⚠️ Gotchas

* **The "Push" Gap:** After `git commit`, your code is **NOT** on the server. It is only on your laptop. If your laptop melts, the code is gone. You must run `git push` to send it to GitHub.
* **Partial Commits:** You can edit 10 files but only `git add` 2 of them. The commit will only contain those 2. This allows for very clean history.

---

### 2. How to "Check Out" Code

In Perforce, you have a Workspace that maps to the server.
In Git, you have two main ways to get code: **Cloning** (Start) and **Pulling** (Update).

#### A. Initial Setup: `git clone`

This is done only once per project. It downloads the **entire repository** (every file, every version, every branch) to your machine.

```bash
git clone https://github.com/YourCompany/vscode-extension.git
cd vscode-extension

```

#### B. Daily Update: `git pull`

This is your morning coffee routine. It fetches new commits from the server and merges them into your current files.

```bash
git pull origin main

```

* `origin`: The alias for the remote server (GitHub).
* `main`: The branch you want to pull.

#### ⚠️ Gotchas

* **Merge Conflicts on Pull:** If you changed `extension.ts` locally, and your coworker also changed it and pushed to the server, `git pull` might fail with a "Conflict." You must resolve it before you can continue (see Section 6).

---

### 3. Check Out a Specific Version (Time Travel)

In Perforce, you might sync to a specific changelist #1234.
In Git, you check out a **Commit Hash** (SHA-1).

#### How to find the Hash

Run `git log` to see the history.

```text
commit a1b2c3d4e5f... (HEAD -> main)
Author: Avantika
Date:   Mon Dec 10 2025
    Fixed memory leak in debug adapter

```

#### The Command

```bash
git checkout a1b2c3d

```

#### ⚠️ The "Detached HEAD" State (Critical Gotcha)

When you do this, Git will warn you: *"You are in 'detached HEAD' state."*

* **What it means:** You are looking at a snapshot in time. You are **not** on a branch.
* **The Danger:** If you start coding here and commit, **your changes do not belong to any branch**. If you switch back to `main`, those commits will be lost (garbage collected) because nothing points to them.
* **The Fix:** If you want to work on an old version (e.g., to fix a bug in V1.0), you **must** create a branch immediately:
```bash
git checkout -b fix-v1-bug a1b2c3d

```



---

### 4. How to Create a Branch (Local vs. Server)

Branches are your workspace for specific tasks.

#### A. Creating a Local Branch

This creates a new label pointing to your current code. It is instant.

```bash
# Create and switch to it immediately
git checkout -b feature/dark-mode

```

#### B. Seeing your Branches

```bash
git branch      # Lists local branches
git branch -r   # Lists remote branches (on GitHub)
git branch -a   # Lists ALL

```

#### C. Publishing to Server (Remote Branch)

Your `feature/dark-mode` is private until you push it.

```bash
# The first time you push a new branch, you must set the "upstream" link
git push -u origin feature/dark-mode

```

* `-u`: Sets "Upstream". Now Git knows that your local `feature/dark-mode` corresponds to `origin/feature/dark-mode`.

#### ⚠️ Gotchas

* **Switching Hazard:** Do not switch branches if you have "dirty" files (uncommitted changes). Git might stop you, or worse, carry those changes over to the new branch. **Always commit or stash** before switching.

---

### 5. What does it mean by "Merge"?

Merging is the act of bringing two divergent histories back together.

**Scenario:**

1. You branched off `main` to create `feature/login`.
2. You made 3 commits.
3. Meanwhile, `main` moved forward (coworkers merged their code).

**The Action:**
You want your `feature/login` changes to be part of `main`.

```bash
# 1. Go to the destination (where you want the code to land)
git checkout main

# 2. Bring the changes IN
git merge feature/login

```

* **Fast-Forward Merge:** If `main` hasn't changed since you left, Git simply moves the `main` pointer forward to your latest commit. Instant and clean.
* **Recursive/True Merge:** If `main` *did* change, Git creates a new "Merge Commit" that ties the two histories together.

---

### 6. How to Resolve Conflicts

This happens when two people edit the **same line of the same file**. Git cannot guess who is right, so it asks you.

#### The Conflict Workflow

1. **The Trigger:** You run `git merge` or `git pull`.
2. **The Error:** Git says: *CONFLICT (content): Merge conflict in extension.ts. Automatic merge failed; fix conflicts and then commit the result.*
3. **The Fix:**
* Open `extension.ts` in VS Code.
* Look for the markers:
```typescript
<<<<<<< HEAD
const maxConnections = 10; // Your change (in main)
=======
const maxConnections = 20; // Incoming change (from feature)
>>>>>>> feature/login

```


* **Edit:** Delete the markers (`<<<`, `===`, `>>>`) and choose the correct code (or combine them).
```typescript
const maxConnections = 20; // You decided 20 is correct

```




4. **The Conclusion:**
* Save the file.
* **Stage it:** `git add extension.ts` (This tells Git "I fixed it").
* **Commit it:** `git commit` (This finishes the merge).



#### ⚠️ Gotchas

* **Panic:** If you mess up the conflict resolution and get confused, you can always abort and start over:
```bash
git merge --abort

```


* **Binary Files:** You cannot resolve conflicts in images or DLLs effectively. You usually have to choose one or the other (`git checkout --ours image.png` or `git checkout --theirs image.png`).