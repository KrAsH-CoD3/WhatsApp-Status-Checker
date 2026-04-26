---
skill_name: "Atomic Git Commits"
version: "1.0.0"
description: >
  Analyzes all uncommitted changes in a Git repository, groups them by logical
  purpose, proposes separate conventional-commit messages for each group, and
  commits them sequentially — producing a clean, atomic commit history.
triggers:
  - "commit my changes"
  - "break commits into separate messages"
  - "organize my commits"
  - "split my changes into commits"
  - "atomic commits"
prerequisites:
  - "The working directory must be a Git repository."
  - "There must be uncommitted changes (staged, unstaged, or untracked files)."
  - "A remote tracking branch should exist (for determining the baseline)."
tags:
  - git
  - version-control
  - commits
  - workflow
  - automation
---

# Atomic Git Commits

Split a batch of uncommitted work into clean, logically separated commits with
conventional commit messages.

---

## Phase 1 — Analyze Changes

Gather the full picture of what has changed since the last pushed commit.

```bash
# 1. Current branch and status
git status

# 2. Full diff of unstaged changes
git diff

# 3. Full diff of staged changes (if any)
git diff --cached

# 4. List untracked (new) files
git ls-files --others --exclude-standard

# 5. Confirm baseline — last commit on the remote
git log -n 1 --oneline origin/<current-branch>..HEAD
```

Read every diff line-by-line. For each changed file, note:
- **What** changed (imports, logic, config, docs, etc.)
- **Why** it changed (new feature, bug fix, refactor, cleanup, etc.)

---

## Phase 2 — Categorize & Plan Commits

### Grouping Rules

1. **Group by logical purpose**, not by file. One file may contribute to
   multiple commits; multiple files may belong to a single commit.
2. **Order commits from foundation → feature → fix → polish:**
   - Infrastructure / dependency changes first
   - New features and capabilities next
   - Bug fixes after
   - Chores, docs, and style last
3. Each commit must leave the codebase in a **valid, non-broken state**.

### Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix      | When to use                                         |
|-------------|-----------------------------------------------------|
| `feat:`     | New feature or capability                           |
| `fix:`      | Bug fix or correction                               |
| `refactor:` | Code restructuring without behavior change          |
| `chore:`    | Maintenance, tooling, config, non-functional change |
| `docs:`     | Documentation only                                  |
| `style:`    | Formatting, whitespace — no logic change            |
| `test:`     | Adding or updating tests                            |
| `perf:`     | Performance improvement                             |
| `ci:`       | CI/CD configuration changes                         |

### Output Format

Present the plan to the user as a numbered list:

```
Commit 1 — <files>
  Message: <type>: <description>
  Covers:  <short explanation>

Commit 2 — <files>
  Message: <type>: <description>
  Covers:  <short explanation>

...
```

**Wait for user confirmation before proceeding.**

---

## Phase 3 — Commit Changes Sequentially

Execute each planned commit in order using one of two strategies depending on
whether the file is fully or partially included in the commit.

### Strategy A — Whole-file commit

All changes in the file belong to this commit.

```bash
git add <file1> <file2> ...
git commit -m "<type>: <description>"
```

### Strategy B — Partial-file commit (split across commits)

A single file contains changes that belong to **different** commits.

1. **Temporarily revert** the lines in the file that belong to *later* commits.
   Use a file-editing tool (e.g., `replace_file_content`) to set those lines
   back to their original (or intermediate) state.
2. **Stage and commit** the file with only the current commit's changes:
   ```bash
   git add <file>
   git commit -m "<type>: <description>"
   ```
3. **Restore** the temporarily reverted lines so they are present in the
   working tree for the next commit.
4. Repeat for each subsequent commit that touches this file.

> **Critical:** After all commits, the file must match the user's final
> intended state exactly.

---

## Phase 4 — Verify

```bash
# Show the new commit history
git log -n <number-of-commits> --oneline

# Confirm no uncommitted changes remain
git status
```

Present the final commit log to the user.

---

## Rules

| #  | Rule                                                                                    |
|----|-----------------------------------------------------------------------------------------|
| 1  | Never mix unrelated changes in a single commit.                                         |
| 2  | After all commits, the working tree must match the user's final state exactly.           |
| 3  | Order commits logically: infrastructure → features → fixes → chores.                    |
| 4  | Always present the plan and wait for confirmation before executing commits.              |
| 5  | New (untracked) files are staged with `git add`; they don't require diff-based splitting.|
| 6  | Each commit should leave the codebase in a buildable / runnable state.                   |

---

## Example

```
User: "commit my changes"

→ Phase 1: git status + git diff → 5 files changed

→ Phase 2: Plan
  Commit 1 — pyproject.toml, src/app/__main__.py
    Message: feat: add CLI entry point for direct module execution
    Covers:  New __main__.py + project.scripts config

  Commit 2 — src/utils/detect.py
    Message: refactor: improve browser detection across platforms
    Covers:  Multi-path detection, fallback methods

  Commit 3 — src/utils/driver.py
    Message: feat: switch to official API for driver downloads
    Covers:  Replace HTML scraping with JSON API, version matching

  Commit 4 — src/config/vars.py, src/utils/driver.py (partial)
    Message: fix: resolve cross-platform driver path and permissions
    Covers:  Dynamic executable name, chmod on Unix

  Commit 5 — src/utils/driver.py (partial)
    Message: chore: add error logging to driver version check
    Covers:  Print exception details on failure

→ Phase 3: Execute commits 1-5 sequentially (using Strategy B for driver.py)

→ Phase 4: git log -n 5 --oneline → show results
```
