---
marp: true
theme: default
paginate: true
footer: Git & GitHub Mastery — Architect View
---

<!-- _class: lead -->
# Git & GitHub Mastery  
## The Architect’s Guide  
### From Perforce to Distributed Version Control

---

## How to Read This Deck
- Slides are **concept-first**, not command-first  
- Focus is on **internal architecture & mental models**  
- Speaker Notes explain *why*, not just *how*  

::: notes
This deck is designed for senior engineers and architects.
Encourage questions about internal mechanics rather than commands.
:::

---

# Phase 1 — Core Architecture
## How Git Actually Works

::: notes
Phase 1 is the most important section.
If this mental model is clear, everything else becomes intuitive.
:::

---

## Distributed vs Centralized (Paradigm Shift)

**Perforce**
- Central server = single source of truth
- Client depends on server for history

**Git**
- Every clone is a full database
- Every developer owns the full history

::: notes
Emphasize trust decentralization.
A Git clone is not a workspace — it is a server replica.
:::

---

## Snapshot Model vs Change Lists

**Perforce**
- Records *what changed*
- Line- and file-difference oriented

**Git**
- Records *how the project looked*
- Full snapshot with structural sharing

::: notes
This slide explains why Git enables cheap branching and rebasing.
Snapshots are the key innovation.
:::

---

## Content-Addressable Storage

- Git stores data by **hash of content**
- Same content → same hash → stored once
- Guarantees integrity & immutability

::: notes
This is effectively a key-value database.
Git is closer to a filesystem than a VCS.
:::

---

## The Three Trees

1. Working Directory  
2. Staging Area (Index)  
3. Repository (.git database)

::: notes
This replaces Perforce’s edit/submit workflow.
Staging is Git’s superpower.
:::

---

## Commit = Immutable Object

A commit contains:
- Snapshot pointer
- Author, time, message
- Parent commit(s)
- SHA-1 hash seal

::: notes
A commit is not an action — it is an object.
Hashes make history tamper-evident.
:::

---

# Phase 2 — Daily Local Workflow

---

## The 3-Step Rocket

1. `git add` — curate
2. `git commit` — snapshot
3. `git push` — publish

::: notes
Only push requires network.
Everything else is local & safe.
:::

---

## Why Atomic Commits Matter

- Easier code review
- Easier rollback
- Easier bisect

::: notes
One logical change per commit.
This is a professional discipline.
:::

---

# Phase 3 — Branching as Pointers

---

## Branches Are Not Directories

- Branch = movable pointer
- ~40 bytes of metadata
- Zero copy cost

::: notes
This explains why you should branch freely.
Fear of branching is a Perforce artifact.
:::

---

## HEAD — The “You Are Here” Marker

- HEAD → branch → commit
- Detached HEAD = commit without branch

::: notes
Detached HEAD is exploration mode.
Commits here must be rescued with a branch.
:::

---

## Merging vs Rebasing

**Merge**
- Preserves history shape
- Adds merge commits

**Rebase**
- Rewrites history
- Produces linear timeline

::: notes
Golden rule: never rebase shared history.
:::

---

# Phase 4 — Remotes & Enterprise Flow

---

## Origin vs Upstream

- `origin` → your writable repo
- `upstream` → authoritative source

::: notes
Remotes are aliases, not servers.
Each developer configures them locally.
:::

---

## Fetch vs Pull

- Fetch = download only (safe)
- Pull = fetch + merge (dangerous)

::: notes
Recommend fetch + rebase for professionals.
:::

---

# Phase 5 — Advanced History Control

---

## Rebase: When and Why

Use rebase to:
- Stay current with main
- Clean local commit history

Never rebase:
- Shared branches
- Published history

::: notes
History rewriting is power — and risk.
:::

---

## Reset vs Revert

- Reset rewrites history
- Revert adds compensating commit

::: notes
Reset is local surgery.
Revert is public-safe.
:::

---

# Phase 6 — Large Repos & Dependencies

---

## Submodules — Linked Repositories

- Parent tracks child commit hash
- Two repos, two histories

::: notes
Push submodule first, parent second.
Most failures come from this mistake.
:::

---

## Git LFS

- Git stores pointer
- LFS stores binary

::: notes
Large binaries must never enter normal Git history.
:::

---

# Phase 7 — GitHub as a Platform

---

## Pull Requests

- Social contract, not Git command
- Review + discussion + merge

::: notes
PRs are about communication, not just code.
:::

---

## GitHub Actions

- Native CI/CD
- Event-driven pipelines

::: notes
Actions replace Jenkins for most teams.
Enterprise teams use self-hosted runners.
:::

---

# Phase 8 — Debugging & Recovery

---

## Git Bisect

- Binary search for bugs
- Requires buildable commits

::: notes
This enforces discipline: every commit must build.
:::

---

## Reflog — Your Safety Net

- Tracks HEAD movement
- Recover lost commits

::: notes
Reflog is local and temporary.
It saves careers.
:::

---

<!-- _class: lead -->
# Final Mental Model

Git is not a version control tool.  
It is a **distributed, content-addressable history database**.

::: notes
End by reinforcing architecture over commands.
Once this clicks, Git stops being scary.
:::

