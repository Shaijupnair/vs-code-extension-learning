Here is the complete compilation of our entire conversation, combined into one continuous reply as requested.

---

### **User:**

Yes Please . Also I need to understand fetch

### **Gemini:**

Here is the breakdown of **`git fetch`** followed by the **Merge Strategies** you will encounter when finishing a Pull Request.

---

#### Part 1: What is `git fetch`? (The Safe Update)

Most people blindly run `git pull`. However, to truly understand Git, you must understand `fetch`.

**The Analogy:**

* **`git fetch`:** Is like **checking your email**. Your phone downloads the list of new emails, but it doesn't open them or force you to read them yet. You can see "Oh, the boss sent 3 emails," but you keep doing your current work.
* **`git pull`:** Is like someone grabbing your hand, forcing you to read the email, and immediately making you type a reply. It updates your files *now*.

**Technical Explanation:**
Remember that for every branch (e.g., `main`), you actually have **two** copies on your laptop:

1. **Local Branch (`main`):** The one you are working on.
2. **Remote-Tracking Branch (`origin/main`):** A hidden "bookmark" that remembers where the server was the last time you checked.

**What `fetch` does:**
It updates the **Remote-Tracking Branch** (`origin/main`) to match the GitHub server. It **does not** touch your working files or your local `main` branch.

**Why use it?**
It is safe. You can run `fetch` anytime. It will never overwrite your work or cause a conflict. It simply lets you see what your teammates have done.

**The Workflow:**

1. `git fetch origin` (Download the news).
2. `git log origin/main` (Read the news: "Ah, Bob changed the login screen").
3. `git merge origin/main` (Apply the news to your code).

> **Equation:** `git pull` = `git fetch` + `git merge`

---

#### Part 2: Merge Strategies (The Green Button)

When your Pull Request is approved on GitHub, you click the "Merge" button. But if you click the **arrow** next to it, you see three options. These determine how history is saved.

**Option 1: Create a Merge Commit (The Standard)**
This is the classic "True Merge."

* **What it does:** It takes all your commits and adds a special "Merge Commit" at the end that ties your branch to `main`.
* **The History:** Looks like a diamond loop. It preserves the exact history of your branch.
* **Graph:**
```text
      A---B---C (Feature)
     /         \
Main: M1-----------M2 (Merge Commit)

```



**Option 2: Squash and Merge (The Cleaner)**
This is the most popular strategy for modern teams.

* **What it does:** It takes all your commits (A, B, C), combines them into **one single commit**, and adds *that* to `main`.
* **The History:** A straight line.
* **Why?** It hides your "wip" and "typo" commits.
* **Graph:**
```text
(Feature branch A, B, C are gone)
Main: M1---M2 (Contains changes from A+B+C combined)

```



**Option 3: Rebase and Merge (The Linear)**
This is for strict "Linear History" projects.

* **What it does:** It takes your commits (A, B, C) and replays them one by one at the end of `main`. It does **not** create a merge commit, but it keeps your individual commits distinct.
* **Graph:**
```text
Main: M1---A'---B'---C'

```



**Recommendation for You:**

1. **For Pulling Updates from Open Source:** Use **Rebase**.
2. **For Your Own Features:** Use **Squash**.

---

### **User:**

Is there anything called sub repo or sub module ? What is it how is it structured ? In that case what is the relation ship with main repo and sub repo? Imaging the I am developing a VS code extension "My Debugger" this requires open source "Debug adaptor" and few other open source projects . I bring those open source projects to my company server . Now can I make sub modules so that these open source repo is submodule of my main VS code extension so that my entire VS code extension is within one source folder

### **Gemini:**

Yes, this is exactly what **Git Submodules** are for.

In Git, a **Submodule** is the standard way to nest one repository inside another.

#### 1. What is a Submodule?

A submodule is a full Git repository buried inside a subdirectory of another Git repository.

* **The Main Repo (Parent):** "My Debugger".
* **The Sub Repo (Child):** "Debug Adapter".

**The Relationship:**
The Parent repository **does not** store the files of the Child. Instead, it stores a **pointer** consisting of two things:

1. **The URL:** Where to download the Child repo.
2. **The Commit Hash:** Exactly *which specific version* of the Child repo to use (e.g., `a1b2c3d`).

#### 2. How it works for your "My Debugger" Project

**Scenario:** You have your main project and you want to put the "Debug Adapter" (which you already mirrored to your company server) inside a folder called `libs/adapter`.

**Step A: Adding the Submodule**
You run this command inside your "My Debugger" root folder:

```bash
git submodule add https://github.com/mycompany/debug-adapter.git libs/adapter

```

**Step B: The Structure on Disk**
Your folder structure will look like one big project:

```text
My-Debugger/
├── src/
├── package.json
├── .gitmodules      <-- The map file
└── libs/
    └── adapter/     <-- The Submodule
        ├── .git     <-- It has its own .git folder!
        ├── src/
        └── README.md

```

#### 3. The Workflow (Crucial Details)

**1. Cloning the Project (The "Gotcha")**
If a new developer runs `git clone My-Debugger`, they will get the `libs/adapter` folder, but **it will be empty**.
They must run:

```bash
git clone --recursive https://github.com/mycompany/My-Debugger.git

```

**2. "Pinning" the Version**

* Submodules are **static**. They do not auto-update.
* If the "Debug Adapter" team releases Version 2.0, your "My Debugger" project **will not care**. It stays locked to Version 1.0 until you explicitly upgrade it.

**3. How to Update the Submodule**
When you *do* want to upgrade the adapter to the latest version:

```bash
cd libs/adapter
git fetch
git checkout main
git pull
cd ../..
git add libs/adapter
git commit -m "Upgraded debug-adapter to latest version"

```

#### 4. Modifying the Submodule (Your specific need)

Since you have mirrored the repo to your company server, you can edit code inside the submodule!

1. **Enter the folder:** `cd libs/adapter`
2. **Make changes:** Edit the code.
3. **Commit (Inside Submodule):** `git commit -am "Fixed bug"`.
4. **Push (Inside Submodule):** `git push origin main`.
5. **Update Parent:** Go back to `My-Debugger` root, add the submodule change, and commit.

---

### **User:**

Now can you explain Phase 3: The Complex Workflow (Your Architecture) In detail

### **Gemini:**

This is the "Pro Level" Git architecture. It combines everything: **Mirroring**, **Branching**, **Rebasing**, and **Submodules**.

### The High-Level Architecture

1. **Public Open Source Repo (Upstream):** The original source. Read-Only.
2. **Company Fork (Origin):** Your company's copy. Read-Write. This is where you store your custom changes.
3. **Main Project Repo:** Your VS Code Extension. It contains a **Submodule** pointing to your Company Fork.

### Step 1: The Setup (One-Time Configuration)

**A. Prepare the Child (The Mirror)**
Create `company/debug-adapter` on your server.

* It should have a `main` branch (your custom version).
* It should have an `upstream-main` branch (clean open source version).

**B. Link them (Add Submodule)**
Inside your Parent repo:

```bash
git submodule add https://github.com/company/debug-adapter.git libs/debug-adapter

```

### Step 2: The Development Workflow (Daily Work)

**Scenario:** You find a bug in the Debug Adapter.

1. **Enter the Submodule:** `cd libs/debug-adapter`
2. **Create a Branch:** `git checkout -b fix/memory-leak`
3. **Code & Commit:** `git commit -am "Fixed memory leak"`
4. **Push to Company Server:** `git push -u origin fix/memory-leak`
5. **Update the Parent Repo:**
* `cd ../..`
* `git add libs/debug-adapter`
* `git commit -m "Updated debug-adapter submodule"`
* `git push origin main`



### Step 3: The Maintenance Workflow (The "Rebase" Update)

**Scenario:** The Open Source project released Version 2.0. You want V2.0 features + your fixes.

1. **Fetch Upstream (Open Source):**
```bash
cd libs/debug-adapter
git fetch upstream

```


2. **Update Clean Branch:**
```bash
git checkout upstream-main
git merge --ff-only upstream/main
git push origin upstream-main

```


3. **Rebase Your Work:**
```bash
git checkout main
git rebase upstream-main

```


* *What happens:* Git updates base to V2.0, and replays your fix on top.


4. **Push the Update:**
```bash
git push --force-with-lease origin main

```



### Summary of the Complexity (The "Gotchas")

1. **The "Unpushed Submodule" Error:** If you push the Parent but forget to push the Submodule, coworkers get an error. **Always push the child first.**
2. **Detached HEAD:** Submodules usually point to a commit, not a branch. Always `git checkout main` inside the submodule before working.

---

### **User:**

Now Explain Phase 4: Release Management (Versioning)

### **Gemini:**

Here is the detailed Versioning and Release Management plan.

### 1. The Strategy: Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH` (e.g., `1.2.5`)

* **MAJOR:** Breaking changes.
* **MINOR:** New features.
* **PATCH:** Bug fixes.

### 2. The Release Workflow (Step-by-Step)

#### Step A: Preparation (The Submodule Lock)

**Critical:** You must stabilize your submodules.

1. **Check the Submodule:** `cd libs/debug-adapter`
2. **Tag the Submodule:** `git tag internal-v1.0` -> `git push origin internal-v1.0`
3. **Commit the Pointer:** In Main Repo, `git add libs/debug-adapter` -> `git commit -m "Locking adapter for release"`

#### Step B: Create the Release Branch

```bash
git checkout -b release/v1.0

```

* **Rule:** NO NEW FEATURES. Only bug fixes.

#### Step C: The Golden Tag (Shipping)

1. **Create the Tag:** `git tag -a v1.0.0 -m "Official Release"`
2. **Push the Tag:** `git push origin v1.0.0`
* This usually triggers your build pipeline.



#### Step D: The Merge Back (Sync)

You fixed bugs in `release/v1.0`. `main` needs those fixes!

```bash
git checkout main
git merge release/v1.0
git push origin main

```

### 3. The "Hotfix" Scenario

**Scenario:** V1.0 is live. Users report a crash. You are already working on V2.0 on `main`.

1. **Time Travel:** `git checkout v1.0.0`
2. **Create Branch:** `git checkout -b hotfix/v1.0.1`
3. **Fix & Release:** Fix bug, tag `v1.0.1`, push.
4. **Cherry Pick:** You need this fix in V2.0 too!
```bash
git checkout main
git cherry-pick v1.0.1

```



---

### **User:**

In this chat I asked several things and you answered them . Now I want you to create a complete reply ( or a doc or md ) combining all these answers such a way that I get the full flow correct .

### **Gemini:**

Here is your complete, consolidated **Master Guide**.

# Transition Guide: Perforce to Git for Complex Projects

## Part 1: The Paradigm Shift

* **Perforce:** Centralized. You "rent" files.
* **Git:** Distributed. You "own" the full library.
* **3 States:** Working Directory -> Staging Area -> Local Repository.

## Part 2: Architecture & Initial Setup (Day 0)

**Step A: Mirror the Open Source Repo**

```bash
git clone --bare https://github.com/opensource/debug-adapter.git temp-repo
cd temp-repo
git push --mirror https://github.com/mycompany/debug-adapter.git
cd .. && rm -rf temp-repo

```

**Step B: Create Your Project with Submodule**

```bash
git clone https://github.com/mycompany/my-extension.git
cd my-extension
git submodule add https://github.com/mycompany/debug-adapter.git libs/adapter
git commit -m "Initial structure"
git push origin main

```

## Part 3: The Daily Workflow

**Starting a Task:**

```bash
git checkout main
git pull origin main
git checkout -b feature/login

```

**Saving Work:**

```bash
git add .
git commit -m "Implemented login"

```

**Sharing Work:**

```bash
git push -u origin feature/login
# Go to GitHub -> Create Pull Request -> Squash and Merge

```

## Part 4: Advanced Workflow (Submodules & Upstream)

**Scenario:** Updating your fork with Open Source changes.

1. `cd libs/adapter`
2. `git fetch upstream`
3. `git checkout main`
4. `git rebase upstream/main` (Replay your patches on top of their new code)
5. `git push --force-with-lease origin main`
6. `cd ../..` (Back to parent)
7. `git add libs/adapter` -> `git commit`

## Part 5: Release Management

1. **Lock Dependencies:** Ensure submodule is on a stable commit.
2. **Branch:** `git checkout -b release/v1.0`
3. **Tag:** `git tag -a v1.0.0`
4. **Publish:** `git push origin v1.0.0`
5. **Sync:** Merge `release/v1.0` back into `main`.

---

### **User:**

what does git push --mirror do

### **Gemini:**

**`git push --mirror`** is the "Force Copy" of the Git world.

It creates an **exact replica** of your local repository on the remote server.

1. **Pushes All Branches & Tags.**
2. **DELETES Extraneous Data:** If the server has a branch that you *don't* have locally, **it deletes it from the server.**

**Analogy:** Copying your entire hard drive to an external drive. If the external drive had files that aren't on your computer, they are wiped out.

**Use Case:** Only for **Initial Import** (Moving a repo from Open Source to your Company). Never use it for daily work.

---

### **User:**

I ran that but it takes long time .. how do I know its working or not ...

### **Gemini:**

It is normal for `git push --mirror` to take a long time if the repo has years of history.

**Why is it silent?**
Git is calculating and compressing objects (CPU intensive).

**How to check:**

1. **Task Manager:** Look for `git.exe`. If CPU/Network is moving, it's working.
2. **Verbose Mode:** If you restart, run `git push --mirror --verbose ...` to see a progress bar.

**Recommendation:** If you see activity, let it run. It can take 20+ minutes for large repos.

---

### **User:**

when I checked in it ran some work flow file and failed

### **Gemini:**

This happens because the Open Source project contains **GitHub Actions** (`.github/workflows`) that are trying to run on your server but fail because you lack their secrets/environment.

**How to Fix It:**

**Option A: Delete the Workflows (Recommended)**

1. `git checkout main`
2. `git rm -r .github/workflows`
3. `git commit -m "Removed upstream CI workflows"`
4. `git push origin main`

**Option B: Disable in Settings**
Go to Repo Settings -> Actions -> Select "Disable actions".

---

### **User:**

git checkout main
fatal: this operation must be run in a work tree

### **Gemini:**

This error happens because you are inside a **Bare Repository** (the one you used for mirroring). It has no files to edit.

**Solution:**

1. `cd ..` (Get out of the bare folder).
2. `rm -rf temp-repo` (Delete it if done).
3. **Clone Normally:** `git clone https://github.com/mycompany/debug-adapter.git`
4. `cd debug-adapter`
5. Now `git checkout main` will work.

---

### **User:**

what dpes this command do git push origin main

### **Gemini:**

**`git push origin main`** uploads your local changes to the server.

* **`git push`**: Send commits.
* **`origin`**: The nickname for your server (`https://github.com/...`).
* **`main`**: The branch you are sending.

**Plain English:** "Take the new work on my `main` branch and upload it to the server nicknamed `origin`."

---

### **User:**

[https://github.com/eclipse-cdt-cloud/cdt-gdb-adapter](https://github.com/eclipse-cdt-cloud/cdt-gdb-adapter) and [https://github.com/eclipse-cdt-cloud/cdt-gdb-vscode](https://github.com/eclipse-cdt-cloud/cdt-gdb-vscode) exists under [https://github.com/eclipse-cdt-cloud](https://github.com/eclipse-cdt-cloud) . How is this achieved is this a sub repo or some kind of space ? In my company repo how can in create something like this ?

### **Gemini:**

What you are seeing is a **GitHub Organization**.

* **Organization:** `eclipse-cdt-cloud` (The "Tenant" or Company).
* **Repository 1:** `cdt-gdb-adapter`
* **Repository 2:** `cdt-gdb-vscode`

These are **siblings**, not sub-repos.

**How to do this:**

1. Create an **Organization** on GitHub (`MyCompanyTech`).
2. Create multiple **Repositories** inside that Organization.
3. Link them using **Submodules** in code if needed.

---

### **User:**

what is git hub project is that same as organization

### **Gemini:**

No.

* **Organization:** The "Building" (Owns the repos).
* **Repository:** The "Filing Cabinet" (Stores the code).
* **GitHub Project:** The **Whiteboard** (Kanban board for task tracking).

You write code in a **Repository**.
You plan work (Jira-style) in a **Project**.
You own both in an **Organization**.

---

### **User:**

what is gist

### **Gemini:**

A **Gist** is a mini-repo for a single file or snippet.
**Use Case:** Sharing a quick script or error log with a coworker without setting up a full repository.

---

### **User:**

how to disable work flow

### **Gemini:**

**Method 1: The "Soft" Disable (UI)**
Repo -> Actions -> Click Workflow -> Click "..." -> **Disable workflow**.

**Method 2: The "Hard" Disable (Delete)**
`git rm -r .github/workflows` -> Commit -> Push.
*Recommended for your Vendor Mirror.*

---

### **User:**

now I have brought the open soruce repo to my company site . I want to bring latest changes of open soruce to my company repo (fork) What is the step by step process in this case .

### **Gemini:**

This is the **Vendor Update** routine.

**Step 1: Get Data**
`git fetch upstream --tags`

**Step 2: Update Clean Mirror**

```bash
git checkout upstream-main
git reset --hard upstream/main
git push origin upstream-main --tags

```

**Step 3: Update Your Product (Rebase)**

```bash
git checkout main
git rebase upstream-main

```

* *If conflicts occur:* Fix files -> `git add .` -> `git rebase --continue`.

**Step 4: Push**
`git push --force-with-lease origin main`

---

### **User:**

what is a sub repository ? how do we create a sub repository when we should use that

### **Gemini:**

A "sub repository" is a **Git Submodule**.

**Concept:** A pointer inside your main repo that links to a specific commit of another repo.

**Use It When:**

1. You need to modify the source code of a dependency.
2. You need strict version locking.

**How to Create:**
`git submodule add <URL> <Path>`

**Gotcha:**
New users must clone with `git clone --recursive`.

---

### **User:**

Can you elaborate on Phase 3: The Complex Workflow (Your Architecture) in the first reply. Clearly elaborate upstream ,origin, merge, push pull request ,sub module ,branch ,clone ,clone recursive ,mirror rebasing , forking,force with lease,bare repo and bare mod,

### **Gemini:**

Here is the glossary within your workflow:

1. **Forking:** Creating your company's copy of an Open Source repo.
2. **Bare Repo:** A folder with only history (no files). Used for **Mirroring** (Copying history 1:1).
3. **Submodule:** Embedding that fork inside your Main Extension repo.
4. **Clone Recursive:** How you download the Extension + Submodule files.
5. **Branch:** Your workspace (`fix/bug`).
6. **Origin:** Your Company Server.
7. **Upstream:** The Open Source Server.
8. **Rebase:** Moving your custom commits on top of new Upstream code.
9. **Force with Lease:** The safe way to overwrite history after rebasing.

---

### **User:**

Can you explain the concept of rebase with an example use case

### **Gemini:**

**Rebase = "Move the Base".**

**Scenario:**

* **Main** has commits A -> B.
* **You** started at A, and made commit C.
* Your history: `A -> C`
* Real history: `A -> B`

**The Rebase:**
You lift your commit C, and place it *after* B.
**Result:** `A -> B -> C`.

**Why?** It creates a straight line of history.
**Use Case:** Updating your feature branch with the latest `main` code before merging.

---

### **User:**

Can you explain the case of The "Detached HEAD": with and example situation

### **Gemini:**

**Concept:** You are looking at a specific commit, not a branch. (You got off the bus and are standing on the street).

**Example:**

1. `git checkout v1.0` (Detached HEAD).
2. You fix a bug and commit.
3. `git checkout main`.
4. **Result:** Your bug fix is LOST because no branch was holding it.

**Fix:** Always create a branch first: `git checkout -b fix/v1-bug`.

---

### **User:**

Now you read all those questions and answers in this chat . List all the topics we covered as bullet points and List all the points we need to learn about git but missed

### **Gemini:**

**Covered:**

* Paradigms (P4 vs Git)
* Architecture (Mirror, Fork, Submodule)
* Workflow (Branch, PR, Rebase)
* Commands (Fetch, Push, Force-push)
* Release (Tags, SemVer)
* Troubleshooting (Bare repo, Workflows)

**Missed (Next Steps):**

* **Git Stash:** Saving messy work.
* **Undoing (Reset/Revert):** Fixing mistakes.
* **Reflog:** Recovering lost commits.
* **Git Blame:** Seeing who wrote what.
* **Interactive Rebase:** Cleaning history.

---

### **User:**

Please tell me about git Stash in detail with an example. Detailed concept and use case

### **Gemini:**

**Git Stash** is your "Emergency Clipboard."

**Scenario:** You are working on `feature-A`. Boss asks for urgent fix on `main`. You can't switch because files are dirty.

**Workflow:**

1. `git stash` (Saves changes, cleans directory).
2. `git checkout main` -> Fix bug -> Commit.
3. `git checkout feature-A`.
4. `git stash pop` (Brings back your changes).

---

### **User:**

Tell me about Release Management . Semantic versioning Release flow and Hotfixes and tagging . Concept and usage case flow

### **Gemini:**

**SemVer:** `Major.Minor.Patch` (`1.2.0`).

**Flow:**

1. **Stabilize:** `git checkout -b release/v1.0`
2. **Tag:** `git tag -a v1.0.0`
3. **Publish:** `git push origin v1.0.0`
4. **Merge Back:** Merge release branch into `main`.

**Hotfix:**

1. `git checkout v1.0.0`
2. `git checkout -b hotfix/v1.0.1`
3. Fix bug -> Tag -> Push.
4. `git cherry-pick v1.0.1` (Copy fix to `main`).

---

### **User:**

Tell me about the merge in details concept and use case

### **Gemini:**

**1. Fast-Forward:**

* Target hasn't moved. Git just slides the pointer forward.
* **Result:** Straight line.

**2. 3-Way Merge (True Merge):**

* Both sides moved. Git combines them into a **Merge Commit**.
* **Result:** Diamond shape.

**When to use:**

* **Merge:** Finishing a large feature.
* **Squash:** Merging small messy commits.
* **Rebase:** Updating local branch.

---

### **User:**

Read all those chat above... I want you to Explain each and every concept... 1 to 13...

### **Gemini:**

**Master Guide: Xtensa Cloud IDE Migration**

**1. Paradigm Shift:** Git is distributed. You have the full history locally. `Push` = Upload. `Commit` = Save locally.
**2. Setup:** Use `clone --bare` + `push --mirror` for initial import. Use `submodule add` to link repos.
**3. Branching:** Never work on `main`. Use `checkout -b`.
**4. Operations:** `Fetch` (download), `Pull` (update), `Rebase` (replay).
**5. Release:** Tag releases. Use Hotfix branches for patches.
**6. Troubleshooting:** Delete `.github/workflows` on forks.
**7. Stash:** Use `git stash` to switch contexts quickly.
**8. Reset vs Revert:** `Reset` rewrites history (Local). `Revert` adds an undo commit (Public).
**9. Reflog:** Use `git reflog` to recover deleted commits.
**10. Ignore:** Use `.gitignore` for `node_modules`.
**11. Blame:** Use `git blame` to find authors.
**12. Interactive Rebase:** Use `rebase -i` to squash commits.
**13. LFS:** Use LFS for large binaries.

---

### **User:**

I want to understand conflict resolution when merging or rebasing or any time. Can you explain in detail what is incoming what is current

### **Gemini:**

**The "Current" vs "Incoming" definitions change based on context.**

**Case 1: Merge** (`git checkout main`, `git merge feature`)

* **Current:** `main` (Where you are).
* **Incoming:** `feature` (What you are pulling).

**Case 2: Rebase** (`git checkout feature`, `git rebase main`)

* **Current:** `main` (The Base).
* **Incoming:** `feature` (YOUR code being replayed).

**Rule:** When rebasing a fork, **"Incoming" is usually YOUR code.**

---

### **User:**

How to set rules on git repository and branches ? For example I want to ensure that every commit to main branch require one or more JIRA item exists . Need to ensure that association How can I do that ?

### **Gemini:**

**Step 1: Branch Protection**
GitHub Settings -> Branches -> Add Rule (`main`).

* Check "Require pull request".
* Check "Require status checks to pass".

**Step 2: GitHub Action (The Enforcer)**
Create `.github/workflows/check-jira.yml`.
Write a script that scans `pull_request.title` for regex `XTENSA-\d+`.

**Result:** If PR title is "Fixed bug", merge is blocked. If "XTENSA-123: Fixed bug", merge is allowed.

---

### **User:**

Github desktop does it allow merging and conflict resolving nicely ? Or VScode is better ? Can you tell me the step by step approach in both cases ? Also I am always confused about "yours' theirs term . In differet context can you explan that ?

### **Gemini:**

**GitHub Desktop vs VS Code**

* **GitHub Desktop:** Good for *starting* a merge. Bad for *resolving* conflicts (it sends you to VS Code anyway).
* **VS Code:** Excellent for resolving. Use the "Accept Incoming" buttons.

**Yours vs Theirs Matrix**

| Context | Yours (Current) | Theirs (Incoming) |
| --- | --- | --- |
| **Merge** | Main (Old Code) | Feature (New Code) |
| **Rebase** | Main (Upstream) | **Feature (YOUR Code)** |

**Tip:** When rebasing your fork to update it, "Accept Incoming" means "Keep MY custom changes".