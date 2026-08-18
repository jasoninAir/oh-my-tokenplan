# Agentrace

> **Every agent action leaves a trace.**
>
> Multi-agent collaboration protocol for AI coding assistants. When one agent hits a quota wall, the next one picks up in 20 seconds — no context lost, no work duplicated.

[English](README.md) | [简体中文](README_zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests: 39 passing](https://img.shields.io/badge/tests-39%20passing-brightgreen.svg)](bin/tests/)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange.svg)](.claude/skills/agentrace/SKILL.md)

---

## The Problem

You use Claude Code for an hour, hit your 5-hour quota, switch to Antigravity, and start explaining the project from scratch. The new agent reads your codebase, asks 20 questions, gets half of them wrong, and you're back to square one.

Or: Agent A writes a feature, you want Agent B to review it, but neither tool has a clean handoff format.

Or: You're on a long-running project. Different days, different agents, different sessions. Nobody remembers what happened yesterday.

**agentrace solves this by turning multi-agent development into a file-system problem.**

## What It Does

| Concern | How agentrace handles it |
|---------|--------------------------|
| Agent A hits a quota wall mid-edit | `bin/agentrace resume` → 20-line handoff briefing for the next agent |
| Review Agent B for Agent A's work | `bin/agentrace new-review S-001` → reviewer writes markdown, no code touched |
| Different agents on different days | All progress in `docs/agentrace/` as markdown; any agent can read and continue |
| "What will break if I edit this function?" | `bin/agentrace impact divide` → AST-based blast-radius analysis |
| Lost changelog | Every status transition auto-appends to Story's changelog |
| State-machine bugs | `bin/agentrace check --strict` validates frontmatter, transitions, references |

## 30-Second Demo

```bash
# Install once (Claude Code Skill + user-level snippet)
git clone https://github.com/jasoninAir/oh-my-tokenplan.git agentrace
cd agentrace
bin/agentrace install

# In any project, initialize
cd ~/your-project
agentrace init

# Tell Claude Code:
#   "Create a story for implementing user login"
#
# Claude Code will:
agentrace new-story --title "implement user login"
# → created: docs/agentrace/stories/S-001-implement-user-login.md

# Tell Claude Code:
#   "I'm taking S-001, start working"
#
# Claude Code will:
agentrace advance S-001 in_progress

# ... code, commit with "(S-001)" in message ...

agentrace advance S-001 in_review

# Tell Antigravity:
#   "Review S-001"
#
# Antigravity will:
agentrace new-review S-001
# → created: docs/agentrace/reviews/R-001-on-S-001.md
# (writes verdict + blockers, doesn't touch src/)

# Back to Claude Code: "Advance S-001 to done based on R-001"
agentrace advance S-001 done
```

## How It Works

```
                user-level snippet (~/.claude/CLAUDE.md)
                  ↓ "AGENTS.md present? Then follow agentrace"
                ┌────────────────────────────┐
                │ project-level (AGENTS.md)  │
                │   - what is this project   │
                │   - current Story table    │
                │   - conventions            │
                └────────────────────────────┘
                  ↓ agent reads these files
                ┌────────────────────────────┐
                │ docs/agentrace/            │
                │   stories/   S-NNN-*.md    │
                │   reviews/   R-NNN-*.md    │
                │   decisions/ D-NNN-*.md    │
                │   inbox/     I-NNN-*.md    │
                │   handbook/  protocol docs │
                └────────────────────────────┘
                  ↓ scripts enforce
                ┌────────────────────────────┐
                │ bin/agentrace              │
                │   advance / check / resume │
                │   new-story / new-review   │
                │   sync / render / impact   │
                └────────────────────────────┘
```

Every artifact is a `.md` file. State machine is enforced by `bin/agentrace check`. Reviewers can't accidentally rewrite code because `bin/agentrace` only writes to `reviews/`, `inbox/`, `decisions/`.

## Concepts

| Concept | Purpose | Example |
|---------|---------|---------|
| **Story** (`S-NNN`) | One unit of work with a state machine: `draft → planned → in_progress → in_review → done` | "implement basic arithmetic" |
| **Review** (`R-NNN-on-S-MMM`) | Reviewer agent's verdict + blockers | "approved" / "changes_requested" |
| **Decision** (`D-NNN`) | ADR-style architectural choice | "use dataclass for Result" |
| **Inbox** (`I-NNN`) | Cross-agent notes that don't block Stories | "TODO: check caching strategy" |
| **Resume** | Post-mortem triage output | dirty files + AST symbols + test probe |

State machine:

```
draft ──→ planned ──→ in_progress ──→ in_review ──→ done
              ↑           ↓                ↓
              └──────── blocked ──────────┘
                  (changes_requested also reverts to in_progress)
```

## CLI Reference

```bash
agentrace init                    # Initialize agentrace in current project
agentrace onboard                 # Semi-automatic scan & onboarding plan generator
agentrace install                 # Install skill + snippet globally
agentrace uninstall               # Reverse install
agentrace install-snippet         # Idempotent snippet install (per-agent)

agentrace new-story --title "…"   # Create S-NNN-<slug>.md with frontmatter
agentrace new-review S-001        # Create R-NNN-on-S-001.md

agentrace advance S-001 in_progress   # State-machine-only transitions
agentrace sync                    # Refresh AGENTS.md active-Story table + impacted_symbols
agentrace check [--strict]        # Validate frontmatter, refs, state machine
agentrace render                  # Generate docs/agentrace/OVERVIEW.md

agentrace resume                  # Post-mortem: dirty workspace + AST + test probe
agentrace triage                  # Alias for resume
agentrace impact <symbol>         # AST-based blast-radius analysis
```

## Installation

### As a Claude Code Skill (recommended)

```bash
git clone https://github.com/jasoninAir/oh-my-tokenplan.git agentrace
cd agentrace
bin/agentrace install
```

This copies the skill to `~/.claude/skills/agentrace/` and appends a snippet to `~/.claude/CLAUDE.md`. After this, any time you `cd` into a project containing `AGENTS.md` + `docs/agentrace/`, Claude Code auto-activates the agentrace skill.

### Per-project

```bash
cd your-project
cp -r /path/to/agentrace/bin ./
cp -r /path/to/agentrace/docs/agentrace ./
cp -r /path/to/agentrace/AGENTS.md /path/to/agentrace/CLAUDE.md /path/to/agentrace/GEMINI.md ./
agentrace init
```

## Worked Example

See `examples/calculator/` — a 60-line Python library that demonstrates the full state machine:

| Story | Path | Demonstrates |
|-------|------|--------------|
| S-001 | draft → planned → in_progress → in_review → done | First-pass approval |
| S-002 | ... → in_review → in_progress → in_review → done | Two-round review with rework |
| S-003 | draft → planned | Long-running planned with TODO in body |
| S-004 | draft → planned → blocked | Blocked on architectural decision |

```bash
cd examples/calculator
../../bin/agentrace check --strict
# → check: passed (4 stories, 3 reviews)

../../bin/agentrace resume
# → 20-line briefing showing current Story + dirty workspace + AST symbols + test status
```

## Constraints Enforced by `agentrace check`

1. **`status:` field is sacred** — only `bin/agentrace advance` may write it. Hand-edits are flagged as errors.
2. **Commit messages must include Story ID** in `(S-NNN)` format. `agentrace sync` harvests them automatically.
3. **Reviewers don't touch code.** They write only to `reviews/`, `inbox/`, `decisions/`. Cross-checked via commit-author vs Story-assignee.
4. **Reviews are append-only.** Old reviews stay as audit trail; never deleted.
5. **All `.md` files must have YAML frontmatter.** Missing fields fail `agentrace check --strict`.

## Supported Agents

| Agent | Adapter file | Status |
|-------|--------------|--------|
| Claude Code | `CLAUDE.md` | Stable |
| Antigravity / Gemini | `GEMINI.md` | Stable |
| Cursor | `adapters/examples/cursor.md` | Example template |
| Any other | See `adapters/README.md` | Add your own |

To add a new agent, write one `<NAME>.md` (≤ 25 lines, mirroring CLAUDE.md), one user-level snippet, and register it in `bin/agentrace install`.

## Design Philosophy

- **File-based > database** — every state transition is a `.md` file; no hidden state
- **Scripts enforce, humans narrate** — `bin/agentrace` blocks illegal transitions
- **Reviewer separation** — code authors and code reviewers are distinct agents; clean permission boundary
- **Two-layer prompts** — user-level snippet sets the discipline; project-level AGENTS.md sets context
- **Zero external dependencies for core** — only Python 3.10+ stdlib + PyYAML
- **Post-mortem, not pre-checkpoint** — agents don't need to know when they'll be interrupted; the next agent reconstructs state from files

## Roadmap

- [ ] v0.2: True AST call-graph analysis (currently v0.1 uses text grep + `ast.FunctionDef`)
- [ ] v0.3: PyPI distribution (`pip install agentrace`)
- [ ] v0.4: VS Code extension auto-detecting AGENTS.md
- [ ] v1.0: Multi-language (Node.js, Rust, Go) demo projects

## Contributing

Issues and PRs welcome. The protocol is intentionally minimal — features that require heavy external dependencies or new tooling are likely to be rejected. The bar is "would a 60-line Python library demo (`examples/calculator`) make sense with this change?"

## License

MIT — see [LICENSE](LICENSE).

## Inspiration

- **Git** — every commit is a file; agentrace's stories are the same
- **Mailing-list archives** — conversations happen in public, durable files
- **Post-mortem culture** — when systems fail, the next responder reads the trace, not the agent's last intent

Built for developers who treat AI agents as collaborators, not oracles.
