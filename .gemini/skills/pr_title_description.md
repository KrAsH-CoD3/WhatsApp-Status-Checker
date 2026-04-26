---
skill_name: "PR Title & Description Generator"
version: "1.0.0"
description: >
  Generates a well-structured pull request title and description by analyzing
  all commits and diffs on the current branch compared to the main remote
  branch. Follows conventional PR formatting standards.
triggers:
  - "generate pr"
  - "create pr description"
  - "write pr title and description"
  - "prepare pull request"
  - "pr summary"
  - "pr ready"
prerequisites:
  - "The working directory must be a Git repository."
  - "The current branch must differ from the default branch (main/master)."
  - "All changes should be committed before generating the PR."
tags:
  - git
  - pull-request
  - github
  - workflow
  - automation
---

# PR Title & Description Generator

Generate a conventional, well-structured pull request title and description
from the commits and diffs on the current feature branch.

---

## Phase 1 — Identify Branches

Determine the current branch and the base branch it will merge into.

```bash
# 1. Current branch name
git branch --show-current

# 2. Determine the default remote branch (main or master)
git remote show origin | grep 'HEAD branch'

# 3. Ensure local knowledge of the remote default branch is up to date
git fetch origin <default-branch>
```

Store:
- `CURRENT_BRANCH` — the feature branch name (e.g., `feat/cross-platform-chromedriver`)
- `BASE_BRANCH` — the remote default branch (e.g., `origin/main` or `origin/master`)

---

## Phase 2 — Gather Context

Collect all commits and the full diff between the branches.

```bash
# 1. List all commits on this branch not on the base branch
git log --oneline <BASE_BRANCH>..HEAD

# 2. Full diff summary (files changed, insertions, deletions)
git diff --stat <BASE_BRANCH>..HEAD

# 3. Full diff for detailed analysis
git diff <BASE_BRANCH>..HEAD
```

For each commit, note:
- The **type** prefix (`feat`, `fix`, `refactor`, etc.)
- The **scope** of the change
- The **intent** behind it

---

## Phase 3 — Generate PR Title

### Title Convention

The PR title should follow this format:

```
<type>: <concise summary of the overall change>
```

#### Rules

| Rule | Detail |
|------|--------|
| Use the **dominant type** from the commits | If most commits are `feat:`, the PR title is `feat:`. If mixed, use the most impactful type. |
| Keep it under **72 characters** | Short enough for GitHub's UI and email notifications. |
| Use **imperative mood** | "Add support for..." not "Added support for..." |
| Capitalize the first word after the prefix | `feat: Add cross-platform ChromeDriver support` |
| No trailing period | |

#### Type Priority (when commits are mixed)

Use the highest-priority type that applies:

1. `feat:` — if any new capability was introduced
2. `fix:` — if the primary goal is a bug fix
3. `refactor:` — if restructuring without new features or fixes
4. `chore:` / `docs:` / `ci:` — for maintenance-only PRs

---

## Phase 4 — Generate PR Description

Use the following template. Fill each section from the analysis in Phase 2.
Omit any section that is not applicable (e.g., skip "Breaking Changes" if there
are none).

````markdown
## Summary

<!-- 2-3 sentence high-level overview of what this PR does and why -->

## Changes

<!-- Bulleted list of the key changes, grouped logically -->

- **<Category>**: <description>
- **<Category>**: <description>

## Commit Log

<!-- Auto-generated from git log; provides reviewers a quick reference -->

| Hash | Message |
|------|---------|
| `<short-hash>` | <commit message> |

## How to Test

<!-- Step-by-step instructions for reviewers to verify the changes -->

1. <step>
2. <step>

## Breaking Changes

<!-- Only include if applicable -->

- <description of what breaks and migration path>

## Related Issues

<!-- Link any relevant issues; omit if none -->

- Closes #<issue-number>
- Related to #<issue-number>
````

### Section Guidelines

| Section | Required | Notes |
|---------|----------|-------|
| Summary | ✅ Yes | Always include; 2-3 sentences max |
| Changes | ✅ Yes | Group related items; use bold category labels |
| Commit Log | ✅ Yes | Auto-generated from `git log --oneline` |
| How to Test | ✅ Yes | Even if it's just "run the app and verify" |
| Breaking Changes | ❌ Optional | Only if something breaks backward compatibility |
| Related Issues | ❌ Optional | Only if issues exist |

---

## Phase 5 — Present & Refine

1. Present the generated **title** and **description** to the user.
2. Ask if any adjustments are needed (wording, scope, missing context).
3. If the user approves, optionally offer to create the PR via the GitHub CLI:

```bash
gh pr create --title "<title>" --body "<description>" --base <default-branch>
```

---

## Rules

| # | Rule |
|---|------|
| 1 | Always analyze the actual diff — never guess what changed. |
| 2 | The title must reflect the **overall intent**, not individual commits. |
| 3 | The description must be useful to a reviewer who has no prior context. |
| 4 | Use markdown formatting consistently in the description. |
| 5 | Keep the summary concise — details belong in the Changes section. |
| 6 | Include the commit log table so reviewers can trace individual changes. |

---

## Example

Given a branch `feat/cross-platform-chromedriver` with these commits:

```
b8570c7 feat: add package entry point and script for easier execution
d9beecf refactor: enhance Chrome version detection for macOS and Linux
17e7dbf feat: implement reliable ChromeDriver fetching via official JSON API
28f4072 fix: ensure cross-platform compatibility for ChromeDriver execution
50687fe chore: add error logging to ChromeDriver version detection
```

### Generated Title

```
feat: Add cross-platform ChromeDriver support with reliable version matching
```

### Generated Description

```markdown
## Summary

This PR adds full cross-platform support for ChromeDriver management,
replacing the fragile HTML scraping approach with the official Chrome for
Testing JSON API. The driver now auto-detects the installed Chrome version
on macOS, Linux, and Windows, downloads a matching ChromeDriver, and sets
the correct file permissions.

## Changes

- **Entry Point**: Added `__main__.py` and a `project.scripts` config for
  direct CLI execution via `whatsapp-status-checker` or `python -m`
- **Chrome Detection**: Expanded macOS and Linux detection to check multiple
  install paths with fallback methods (`mdfind`, `shutil.which`)
- **Driver Downloads**: Migrated from BeautifulSoup HTML scraping to the
  official JSON API at `chrome-for-testing` for reliable, version-matched
  downloads
- **Cross-Platform**: Dynamic executable naming (`chromedriver` vs
  `chromedriver.exe`) and automatic `chmod +x` on Unix systems
- **Error Handling**: Added descriptive error logging when driver version
  detection fails

## Commit Log

| Hash | Message |
|------|---------|
| `b8570c7` | feat: add package entry point and script for easier execution |
| `d9beecf` | refactor: enhance Chrome version detection for macOS and Linux |
| `17e7dbf` | feat: implement reliable ChromeDriver fetching via official JSON API |
| `28f4072` | fix: ensure cross-platform compatibility for ChromeDriver execution |
| `50687fe` | chore: add error logging to ChromeDriver version detection |

## How to Test

1. Run `uv run -m whatsapp_status_checker` on macOS or Linux
2. Verify ChromeDriver is downloaded automatically and the app starts
3. Confirm no `beautifulsoup4` import errors occur
```
