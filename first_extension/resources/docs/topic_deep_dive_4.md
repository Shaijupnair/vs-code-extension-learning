### Topic Rebase
This is one of the most difficult concepts for Perforce users because Perforce doesn't really have an equivalent.

In Perforce, history is immutable (once submitted, it's stone). In Git, **Rebase** allows you to rewrite history to make it look cleaner.

### 1. The Concept: "Changing the Base"

Imagine your code history is a stack of building blocks.

* **The Base:** The block you started building on (e.g., Version 1.0).
* **Your Work:** The blocks you stacked on top (e.g., "My Fix A", "My Fix B").

**The Problem:**
While you were building "Fix A" and "Fix B" on top of **Version 1.0**, the Open Source team released **Version 2.0**.
Your stack is now built on an old base.

**The Solution (Rebase):**
You pick up your blocks ("Fix A", "Fix B"), walk over to the new **Version 2.0** block, and place yours on top of it.
To the outside world, it looks like you started working *after* Version 2.0 was released.

---

### 2. Merge vs. Rebase (Visualized)

Let's look at the difference.

**The Starting State:**

```text
      A---B  (Your Feature)
     /
Main: M1---M2 (Updates from Server)

```

* You started at **M1**.
* You made **A** and **B**.
* Meanwhile, the server added **M2**.

#### Option A: `git merge` (The "True" History)

Git creates a new "Merge Commit" that ties the two paths together.

```text
      A---B---C (Merge Commit)
     /       /
M1-------M2

```

* **Pros:** It preserves the exact history of when things happened.
* **Cons:** It creates a "Diamond" shape. If you do this often, your history looks like "Guitar Hero" tracks—messy and hard to follow.

#### Option B: `git rebase` (The "Clean" History)

Git cuts off your branch, moves it, and replays your work on top of M2.

```text
          A'---B' (Your Feature)
         /
M1---M2 (Main)

```

* **Result:** A perfectly straight line.
* **Note:** Your commits are renamed **A'** and **B'** because they have new Hashes (since their parent changed from M1 to M2).

---

### 3. Under the Hood: What Rebase Actually Does

When you run `git checkout feature` then `git rebase main`, Git performs these 3 steps automatically:

1. **Rewind:** It temporarily removes your commits (A and B) and saves them as "patches."
2. **Update:** It forces your branch to look exactly like the current `main` (M2).
3. **Replay:** It takes your saved patches (A and B) and tries to apply them one by one onto the new end.
* *Git applies A.* (If conflict, it pauses. You fix it. You run `git rebase --continue`).
* *Git applies B.*
* *Done.*



---

### 4. When should you use Rebase?

#### Case 1: The "Downstream" Workflow (YOUR EXACT USE CASE)

You are maintaining a custom version of an Open Source project.

* **Why Rebase?** You want your custom changes to always float *on top* of the open source code.
* If you used Merge, every time the Open Source repo updated, you would create a merge commit. After a year, your history would be a tangled mess of "Merged upstream 1.0", "Merged upstream 1.1".
* **With Rebase:** Your history always looks like: `[Open Source History] -> [Your Custom Patches]`. It is clean and easy to debug.

#### Case 2: Cleaning up a Local Feature

You are working on a private feature branch. You made 10 messy commits ("wip", "typo", "fixing bug").

* Before you push to the team server, you rebase (specifically "Interactive Rebase") to squash them into one clean commit. This makes you look like a very tidy developer.

---

### 5. The Golden Rule: When NOT to Rebase

**NEVER rebase a branch that other people are using.**

Remember: **Rebase changes the Commit ID (Hash).**

**The Disaster Scenario:**

1. You push `feature-login` to the server (Commit ID: `123`).
2. Your colleague pulls it and starts working on top of it.
3. You decide to `rebase` `feature-login`. Your commit ID changes to `999`. You force push it.
4. **Result:** Your colleague is now basing their work on `123`, which essentially *no longer exists* in your version. When they try to pull, Git will explode with conflicts and duplicate history.

**Rule of Thumb:**

* Is the branch **Private** (only on your machine)?  Safe to Rebase.
* Is the branch **Public** (pushed to shared team repo)?  **Do NOT Rebase.** Use Merge.

### Summary for your VS Code Extension

For your specific architecture (Open Source Core + Your Custom Extensions):

1. **Update Strategy:** Always use **Rebase** when pulling updates from the Open Source `upstream`.
* Command: `git pull --rebase upstream main` (or the manual fetch+rebase steps we practiced).
* *Goal:* Keep your custom patches at the very tip of the history.


2. **Team Strategy:** When merging your team's completed features into your company's `main` branch, use **Merge**.
* *Goal:* Preserve the history of who did what and when.