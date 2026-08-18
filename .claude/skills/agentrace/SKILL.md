---
name: agentrace
description: |
  Multi-agent collaboration protocol — every agent action leaves a traceable artifact (Story, Review, Decision, Inbox note).
  Use when the user mentions "story / S-NNN / advance / review / new-story / onboard / set up agentrace" or works in any project that contains AGENTS.md + docs/agentrace/.
  Also auto-activate when the project has README.md / package.json / pyproject.toml but NO AGENTS.md (suggest onboarding).
---

# agentrace — Multi-Agent Collaboration Protocol

agentrace turns multi-agent development from a coordination problem into a file-system problem. Every state transition, every review, every architectural decision becomes a markdown file under `docs/agentrace/`. Any agent — Claude Code, Antigravity, Gemini, Cursor — can read those files and pick up exactly where the previous agent left off.

## When to Activate

Auto-activate when **any** of the following is true:

1. Current directory contains `AGENTS.md` and `docs/agentrace/`
2. User says: "start a story", "advance S-001", "review this", "agentrace resume", "create story for …", "where did I leave off?", **"onboard this project"**, **"set up agentrace"**, **"new project"**
3. A git commit message contains `(S-NNN)` referencing a Story ID
4. **Project has `README.md` / `package.json` / `pyproject.toml` etc. but NO `AGENTS.md`** → prompt user about onboarding (see §Onboarding below)
5. A user-level `agentrace` snippet is installed at `~/.claude/CLAUDE.md`

## Onboarding (semi-automatic)

When you detect a project that has source code but no `AGENTS.md`:

1. **Ask the user ONCE**: "This project doesn't have agentrace set up yet. Want me to onboard it? (I'll scan the code, infer modules, create Stories, and fill AGENTS.md — no more questions after that.)"
2. **If user agrees**, run `bin/agentrace onboard` and **do NOT ask further questions**. The flow is fully automatic from there:
   - `agentrace init` creates `AGENTS.md` + `docs/agentrace/` skeleton
   - Heuristic scan writes `.agents/onboarding-plan.yaml` with candidate modules
   - You (the LLM) read the plan + `README.md` + recent git log
   - For each candidate, infer:
     - **Real title** (e.g. `src/auth` → "user authentication")
     - **Initial status** (commits in last 7 days → `in_progress`; never touched → `planned`; stale → `done`)
     - **Scope description** (1-2 sentences)
   - Run `bin/agentrace new-story --title "<real title>"` for each, then patch the generated frontmatter with the inferred status / scope
   - Run `bin/agentrace sync` to refresh AGENTS.md table
   - Delete `.agents/onboarding-plan.yaml` (it's transient)
3. **If user declines**, do nothing this session. Re-prompt next time.

**Onboarding never rewrites git history.** Old commits stay as-is. `related_commits` is backfilled by future `agentrace sync`.

## Core Concepts

| Concept | File | Lifecycle |
|---------|------|-----------|
| **Story** | `docs/agentrace/stories/S-NNN-<slug>.md` | `draft → planned → in_progress → in_review → done` |
| **Review** | `docs/agentrace/reviews/R-NNN-on-S-MMM.md` | verdict: `approved` / `changes_requested` / `needs_discussion` |
| **Decision** | `docs/agentrace/decisions/D-NNN-<slug>.md` | ADR-style: `proposed → accepted → deprecated` |
| **Inbox** | `docs/agentrace/inbox/I-NNN-<slug>.md` | `open → hold / wontfix / done` |

## Commands (CLI: `bin/agentrace`)

```bash
agentrace init                    # initialize agentrace in a project (writes AGENTS.md + templates)
agentrace install                 # install skill + user-level snippet globally
agentrace install-snippet         # idempotently install user-level snippet only
agentrace new-story --title "…"   # create S-NNN-<slug>.md with frontmatter filled
agentrace new-review S-001        # create R-NNN-on-S-001.md for review
agentrace advance S-001 in_progress   # state machine: only legal transitions allowed
agentrace resume                  # post-mortem triage: dirty workspace + AST symbols + test probe
agentrace impact <symbol>         # blast-radius analysis via Python ast
agentrace sync                    # refresh AGENTS.md "active stories" table + write impacted_symbols
agentrace check [--strict]        # validate frontmatter, references, state machine integrity
agentrace render                  # generate docs/agentrace/OVERVIEW.md grouped by status
```

## Standard Workflow (the 30-second handoff)

### 1. Pick up a Story
```bash
# Detect existing project
ls AGENTS.md docs/agentrace/

# See what's active
agentrace sync && head -30 AGENTS.md
```

### 2. Read + claim
1. Read `AGENTS.md` (≤ 80 lines)
2. Read `docs/agentrace/stories/S-NNN-*.md` for the Story you'll work on
3. Set `assignee:` in frontmatter, then advance state:
```bash
agentrace advance S-001 in_progress
```

### 3. Implement + commit
```bash
# code...
git add .
git commit -m "feat: implement basic arithmetic (S-001)"
```

### 4. Submit for review
```bash
agentrace advance S-001 in_review   # auto-appends changelog with your commits
```

### 5. Hand off to a Reviewer agent
Reviewer creates `docs/agentrace/reviews/R-001-on-S-001.md` with verdict.

### 6. Iterate or close
- `approved` → `agentrace advance S-001 done`
- `changes_requested` → Story auto-reverts to `in_progress`
- `needs_discussion` → Reviewer creates a Decision (D-NNN)

## Post-Mortem Triage (`agentrace resume`)

When a quota exhaustion / 429 / sudden disconnect happens, the next agent runs:

```bash
agentrace resume
```

Output is a 20-line handoff briefing:
```
=================== Post-Mortem Triage Briefing ===================
【Active Story】: S-001 (implement basic arithmetic)
【Workspace】:    3 dirty files
  - src/calculator/core.py  [M]
【CodeGraph】:    function `divide(a, b)` — 2 callers
【Test Probe】:   FAIL: test_div_by_zero (ZeroDivisionError uncaught)
【Suggestion】:   Fix divide() to raise the typed exception.
========================================================================
```

No agent needs to know it was the previous one — just read the briefing and continue.

## Constraints (enforced by `agentrace check`)

1. **Status field is sacred.** Only `agentrace advance` may write it. Hand-edits are flagged as errors.
2. **Commit messages must include Story ID** in `(S-NNN)` format. `agentrace sync` harvests them automatically.
3. **Reviewers don't touch code.** They write to `reviews/`, `inbox/`, `decisions/` only. Boundary enforced via commit-author vs Story assignee check.
4. **Stories and Reviews are append-only.** Older reviews are preserved as audit trail. Don't delete them.
5. **All .md files must have YAML frontmatter.** Missing fields fail `agentrace check --strict`.

## Failure Modes & Recovery

| Symptom | Cause | Recovery |
|---------|-------|----------|
| `invalid transition` error | tried to skip a state (e.g. draft → done) | walk through intermediate states |
| `requires assignee` error | tried `→ in_progress` without filling `assignee:` | edit frontmatter, fill assignee, retry |
| Story stuck in `blocked` | waiting on `D-NNN` decision | implement the decision, then advance |
| Resume shows test FAIL | predecessor agent crashed mid-fix | investigate the FAIL message in briefing, fix, commit, advance |

## Example Triggers

| User says | Action |
|-----------|--------|
| "start a story for adding user login" | `agentrace new-story --title "adding user login"` |
| "I want to work on S-001" | read story → fill `assignee:` → `agentrace advance S-001 in_progress` |
| "review S-001" | `agentrace new-review S-001` then write review body |
| "advance S-001 to review" | `agentrace advance S-001 in_review` |
| "where did I leave off?" (mid-disconnect) | `agentrace resume` |
| "what will change if I edit `divide`?" | `agentrace impact divide` |
| "is this project healthy?" | `agentrace check --strict` |

## Style

- Chinese or English OK; default to user's language
- No emoji in committed files (enforced by CLAUDE.md convention)
- TODOs use `<!-- TODO: ... -->` comments
- Commit message format: `<type>: <description> (S-NNN)`

## Where to Learn More

- Protocol spec: `docs/superpowers/specs/2026-08-17-multiagent-protocol-design.md`
- Implementation plan: `docs/superpowers/plans/2026-08-17-multiagent-protocol.md`
- Story lifecycle: `docs/agentrace/handbook/story-lifecycle.md`
- Review protocol: `docs/agentrace/handbook/review-protocol.md`
- Relay & triage: `docs/agentrace/handbook/relay-and-triage.md`