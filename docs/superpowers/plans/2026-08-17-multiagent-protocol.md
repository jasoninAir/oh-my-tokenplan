# agentrace Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 agentrace v0.1 — 一套 file-based 的多 Agent 协作模板，让 Claude Code / Antigravity / 其他 Agent 接入任意派生项目后通过 markdown 即可上手开发、接力、Review，并在 Token 额度突发熔断时通过 Post-Mortem Triage 与 CodeGraph 拓扑感知实现 1 秒零损接力。

**Architecture:** 单仓库即模板。两层提示词（用户级 `~/.claude/CLAUDE.md` 注入纪律 + 项目级 `AGENTS.md` 注入上下文），所有 Story / Review / Decision 以 markdown 文件存于 `docs/agentrace/`，由 `bin/agentrace`（Python 3.10+）薄 CLI 强制状态机、一致性校验、事后现场勘查与代码影响面分析。

**Tech Stack:**
- 文档：Markdown + YAML frontmatter
- CLI：Python 3.10+（仅标准库 AST + PyYAML + 外部 CodeGraph/pytest 探针）
- 测试：pytest
- 示例：Python mini 计算器库（dataclass + pytest）

**Spec:** `docs/superpowers/specs/2026-08-17-agentrace-protocol-design.md`

## Global Constraints

- 仓库根目录：`/Users/jason/python/AI/agentrace/`
- Python 版本：3.10+
- 仅依赖标准库 + PyYAML（PyYAML 已在 conda ai 环境默认存在）
- commit 格式：`<type>: <description>`（type ∈ feat / fix / refactor / docs / test / chore）
- 中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释
- 文件 ID：`S-NNN` / `R-NNN` / `D-NNN` / `I-NNN`（3 位补零，全局递增，由 `bin/agentrace` 自动分配）
- 不手改 `status:` 字段，必须 `bin/agentrace advance`
- 适配器 ≤ 25 行，AGENTS.md ≤ 80 行
- 所有 .md 文件必须有 YAML frontmatter

## File Structure

```
agentrace/
├── AGENTS.md                          # Task 1
├── README.md                          # Task 0
├── LICENSE                            # Task 0
├── .gitignore                         # Task 0
├── CLAUDE.md                          # Task 2
├── GEMINI.md                          # Task 2
├── adapters/
│   ├── README.md                      # Task 28
│   ├── snippets/
│   │   ├── claude.md                  # Task 29
│   │   └── antigravity.md             # Task 29
│   └── examples/
│       └── cursor.md                  # Task 30
├── docs/agentrace/
│   ├── handbook/
│   │   ├── story-lifecycle.md         # Task 3
│   │   ├── review-protocol.md         # Task 4
│   │   ├── relay-and-triage.md        # Task 5b
│   │   └── conventions.md             # Task 5
│   ├── stories/_TEMPLATE.md           # Task 6
│   ├── reviews/_TEMPLATE.md           # Task 7
│   ├── inbox/README.md                # Task 8
│   ├── decisions/D-001-use-yaml-frontmatter.md  # Task 8
│   └── plan/ROADMAP.md                # Task 9
├── bin/
│   ├── agents                         # Task 19 骨架 → 27b 命令
│   └── tests/                         # Task 19
│       ├── conftest.py
│       ├── fixtures/
│       │   └── sample_project/        # 测试用 mini 项目
│       ├── test_new_story.py
│       ├── test_new_review.py
│       ├── test_advance.py
│       ├── test_sync.py
│       ├── test_check.py
│       ├── test_render.py
│       ├── test_resume.py             # Task 26b
│       ├── test_impact.py             # Task 26c
│       └── test_install_snippet.py
├── examples/calculator/
│   ├── pyproject.toml                 # Task 10
│   ├── README.md                      # Task 13
│   ├── src/calculator/
│   │   ├── __init__.py                # Task 10
│   │   └── core.py                    # Task 10-12
│   ├── tests/
│   │   ├── __init__.py                # Task 10
│   │   └── test_core.py               # Task 11-12
│   └── docs/agentrace/
│       ├── stories/
│       │   ├── S-001-basic-arithmetic.md   # Task 14
│       │   ├── S-002-power-and-errors.md   # Task 15
│       │   ├── S-003-write-readme.md       # Task 17
│       │   └── S-004-cache-last-result.md  # Task 18
│       ├── reviews/
│       │   ├── R-001-on-S-001.md           # Task 14
│       │   ├── R-002-on-S-002.md           # Task 15
│       │   └── R-003-on-S-002.md           # Task 16
│       ├── decisions/D-001-use-dataclass.md  # Task 13
│       └── plan/ROADMAP.md                   # Task 18
└── .claude/skills/agentrace/
    └── SKILL.md                       # Task 31
```

---

## Phase 0: 项目根脚手架

### Task 0: 仓库根初始化

**Files:**
- Create: `/Users/jason/python/AI/agentrace/.gitignore`
- Create: `/Users/jason/python/AI/agentrace/LICENSE`
- Create: `/Users/jason/python/AI/agentrace/README.md`

**Step 1: 检查目录是否已有 git 仓库**

Run: `git -C /Users/jason/python/AI/agentrace rev-parse --is-inside-work-tree 2>/dev/null && echo "EXISTS" || echo "MISSING"`
Expected: `MISSING`（如果是 EXISTS，跳过 git init）

**Step 2: 初始化 git（如果需要）**

```bash
git init
```

**Step 3: 创建 `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
```

**Step 4: 创建 `LICENSE`（MIT）**

```
MIT License

Copyright (c) 2026 agentrace contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 5: 创建仓库根 `README.md`**

````markdown
# agentrace

> 多 Agent 协作的 file-based 协议。
> Claude Code、Antigravity 或其他 Agent 接入任何派生项目，靠 markdown + 薄脚本就能交接。

## 一句话

把项目开发和 Agent 解耦：所有上下文、进度、Review 都写在 `docs/agentrace/` 的 markdown 里，
任意 Agent cd 进项目读完 AGENTS.md 就能上手，不依赖任何代码层 API。

## 5 分钟上手

### 在新项目使用本模板

```bash
mkdir my-project && cd my-project
git init
cp -r /path/to/agentrace/. .
bin/agentrace install-snippet   # 把通用纪律装到 ~/.claude/CLAUDE.md
```

然后编辑 `AGENTS.md` 填项目简介，`bin/agentrace new-story` 开始第一个 Story。

### 接手一个已有项目（agentrace 派生）

1. 读 `AGENTS.md`（≤ 80 行）
2. 读 `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. 读 `docs/agentrace/handbook/story-lifecycle.md` 了解状态机
4. 跑 `bin/agentrace check` 确认环境干净
5. 接手：填 `assignee`，调 `bin/agentrace advance <id> in_progress`

## 目录约定

| 路径 | 作用 |
|------|------|
| `AGENTS.md` | 项目主入口（single source of truth） |
| `CLAUDE.md` / `GEMINI.md` | Claude Code / Antigravity 适配器（≤ 25 行） |
| `adapters/` | 适配器模板 + 用户级片段 |
| `docs/agentrace/stories/` | 一个 Story 一个 .md |
| `docs/agentrace/reviews/` | 一个 Review 一个 .md |
| `docs/agentrace/decisions/` | 一个 Decision 一个 .md (ADR 风格) |
| `docs/agentrace/inbox/` | 跨 Agent 临时便条 |
| `docs/agentrace/handbook/` | 协议详细文档 |
| `bin/agentrace` | 薄脚本 CLI |
| `examples/calculator/` | 完整状态机路径示例 |

## 设计原则

- **File-based 优先**：状态、进度、Review 全部 markdown，无数据库
- **状态机由脚本强制**：不能手改 status，必须 `bin/agentrace advance`
- **Reviewer 只提建议**：不直接改 src/
- **两层提示词**：用户级纪律 + 项目级上下文，互不污染
- **适配器极薄**：核心约束都在 AGENTS.md，新增 Agent 工具只需加 25 行

## 详细文档

- 状态机：`docs/agentrace/handbook/story-lifecycle.md`
- Review 协议：`docs/agentrace/handbook/review-protocol.md`
- 命名约定：`docs/agentrace/handbook/conventions.md`
- 适配器开发：`adapters/README.md`

## 状态

v0.1（设计完成，实现进行中）

## License

MIT
````

**Step 6: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add .gitignore LICENSE README.md
git commit -m "chore: init repo with .gitignore, LICENSE, README"
```

---

## Phase 1: 协议根入口

### Task 1: AGENTS.md（项目宪法）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/AGENTS.md`

**Step 1: 创建 AGENTS.md**

````markdown
# AGENTS.md — agentrace模板

> 本文件是 agentrace 模板的 single source of truth。
> CLAUDE.md / GEMINI.md 只是适配器，所有约束都源自本文件。
> 任何 Agent 接手 agentrace 派生项目：先 Read 本文件，再 Read 当前激活 Story。

## 项目简介

agentrace 是一套多 Agent 协作的 file-based 协议模板。它本身既是模板仓库，也是"被自己协议管理"的实例——本仓库的 Story / Review 同样存于 `docs/agentrace/`。

## 架构速览

```
agentrace/
├── AGENTS.md        ← 项目宪法（你正在读）
├── CLAUDE.md / GEMINI.md   ← 适配器（薄，引用本文件）
├── adapters/        ← 用户级注入片段
├── docs/agentrace/     ← 协作主干（stories / reviews / decisions / inbox / handbook）
├── bin/agentrace       ← 薄 CLI，强制状态机
└── examples/calculator/    ← 完整状态机路径示例
```

详细：spec 文件 `docs/superpowers/specs/2026-08-17-agentrace-protocol-design.md`

## 当前激活 Story

<!-- bin/agentrace sync 维护这段；Agent 不要手动编辑 -->
| ID | 标题 | 状态 | 负责人 |
|----|------|------|--------|
| — | （暂无，按 bin/agentrace new-story 创建第一个 Story） | — | — |

完整列表见 `docs/agentrace/stories/`。

## 路线图

本季度目标：把 agentrace v0.1 从设计稿变成可运行的模板。

- [x] 设计 spec（2026-08-17）
- [ ] bin/agentrace CLI 实现
- [ ] examples/calculator 完整数据
- [ ] 适配器片段 + install-snippet 幂等机制
- [ ] 自检：bin/agentrace check --strict 全通过

## 工作流（给新 Agent 的最短路径）

1. **热接力探测**：先跑 `bin/agentrace resume`，若存在中断的脏工作区或测试报错，直接获取现场简报接力
2. Read 本文件
3. Read `docs/agentrace/handbook/story-lifecycle.md`（状态机详细）
4. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
5. 跑 `bin/agentrace check` 确保环境干净
6. 干活：commit message 含 `(S-NNN)`；可用 `bin/agentrace impact` 分析改动影响面
7. 调 `bin/agentrace advance <id> in_review` 提交 review
8. Reviewer Agent 写 `docs/agentrace/reviews/R-NNN-on-S-MMM.md`

## 约定

- commit message: `<type>: <description> (S-NNN)`
- 中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释
- Review 写在 `docs/agentrace/reviews/`，不直接改代码
- 不手改 `status:`，必须 `bin/agentrace advance`
- 新 ID 由 `bin/agentrace new-*` 自动分配，禁止手写

## 已知坑

- `bin/agentrace install-snippet` 的 Antigravity 路径待官方文档验证
- PyYAML 已是 conda ai 环境默认依赖，但其他环境需 `pip install pyyaml`

## 详细文档

- 状态机：`docs/agentrace/handbook/story-lifecycle.md`
- Review 协议：`docs/agentrace/handbook/review-protocol.md`
- 接力与现场还原：`docs/agentrace/handbook/relay-and-triage.md`
- 命名 / 格式 / commit：`docs/agentrace/handbook/conventions.md`
- 决策记录：`docs/agentrace/decisions/`
- Inbox：`docs/agentrace/inbox/`
- 路线图：`docs/agentrace/plan/ROADMAP.md`
- 适配器开发：`adapters/README.md`
- 设计文档：`docs/superpowers/specs/2026-08-17-agentrace-protocol-design.md`
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add AGENTS.md
git commit -m "docs: add AGENTS.md as project single source of truth"
```

---

### Task 2: CLAUDE.md / GEMINI.md 适配器

**Files:**
- Create: `/Users/jason/python/AI/agentrace/CLAUDE.md`
- Create: `/Users/jason/python/AI/agentrace/GEMINI.md`

**Step 1: 创建 CLAUDE.md**

````markdown
# CLAUDE.md — Claude Code 适配器

<!-- 主约定在 ./AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1。

## 工作流（接入 30 秒）

1. 跑 `bin/agentrace resume` 探测是否存在突发中断的脏工作区与测试断点
2. Read `AGENTS.md`
3. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
4. `bin/agentrace check` 一次确保环境干净
5. 干活，commit message 含 `(S-NNN)`；关键改动前可用 `bin/agentrace impact` 分析影响面

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`
- 不改 `src/` 等代码
- 不改 `stories/<id>.md` 的 `status:` 字段（必须 `bin/agentrace advance`）

## Claude Code 风味

- 优先用 `Skill` 工具调预置工作流（`.claude/skills/agentrace/SKILL.md`）
- 派子任务用 `Agent` 工具
- 改文件前先 `Grep` 定位，避免盲改

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。
````

**Step 2: 创建 GEMINI.md**

````markdown
# GEMINI.md — Antigravity 适配器

<!-- 主约定在 ./AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1。

## 工作流（接入 30 秒）

1. 跑 `bin/agentrace resume` 探测是否存在突发中断的脏工作区与测试断点
2. Read `AGENTS.md`
3. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
4. `bin/agentrace check` 一次确保环境干净
5. 干活，commit message 含 `(S-NNN)`；关键改动前可用 `bin/agentrace impact` 分析影响面

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`
- 不改 `src/` 等代码
- 不改 `stories/<id>.md` 的 `status:` 字段（必须 `bin/agentrace advance`）

## Antigravity 风味

- 结合 CodeGraph MCP / AST 拓扑进行符号调用链与影响面分析
- 调试 py 程序在指定 Python 环境（如 `conda activate datasci`）

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。
````

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add CLAUDE.md GEMINI.md
git commit -m "docs: add Claude Code and Antigravity adapters"
```

---

### Task 3: handbook/story-lifecycle.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/handbook/story-lifecycle.md`

**Step 1: 创建文件**

````markdown
# Story 生命周期

## 状态机

```
draft → planned → in_progress → in_review → done
              ↑           ↓              ↓
              └───────────┴── blocked ───┘
                 (changes_requested 也回 in_progress)
```

完整转换表：

| from → to | 触发者 | 附加条件 |
|-----------|--------|----------|
| draft → planned | author | `## 验收标准` 章节 ≥ 1 条 |
| planned → in_progress | 任何人 | `assignee:` 已填 |
| in_progress → in_review | assignee | `related_commits` ≥ 1 |
| in_review → done | 任何人 | 关联 review `verdict: approved` |
| in_review → in_progress | 自动 | 关联 review `verdict: changes_requested` |
| any → blocked | 任何人 | `blocked_by:` 非空 |
| blocked → 原状态 | 解除者 | 删 `blocked_by:` |

唯一改 `status:` 的方式：`bin/agentrace advance <id> <new>`。
手改会被 `bin/agentrace check` 报错。

## 阻塞与解锁

blocked 状态必须有：
- `blocked_by:` 字段，说明卡在哪
- 实现日志追加一行 `@<角色> 请帮助`（@antigravity / @claude-impl-A / @human）

解锁方式：
- 关联的 D-NNN 决策落地后，删 `blocked_by:` 并 `advance` 回原状态
- 或 `assignee` 主动说明已自行解决

## changelog 维护

每个状态转换**必须**对应一行 changelog：

```
- 2026-08-17 10:00  status: in_progress → in_review
                  commits: [abc1234]
                  @antigravity 请 review
```

`bin/agentrace advance` 自动追加，手写无效。

## 工作流示例

**Agent A 接 S-001**：

```bash
# 1. 接手
bin/agentrace advance S-001 in_progress   # status: planned → in_progress

# 2. 写代码
git commit -m "feat: implement basic arithmetic (S-001)"

# 3. 提交 review
bin/agentrace advance S-001 in_review    # status: in_progress → in_review
                                       # 自动写 changelog，列 commits
```

**Agent B 接手 review**：

```bash
# 1. 写 review
# 创建 docs/agentrace/reviews/R-001-on-S-001.md，verdict: approved

# 2. Agent A 据此 advance 到 done
bin/agentrace advance S-001 done         # 自动校验有关联 approved review
```
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/handbook/story-lifecycle.md
git commit -m "docs: add story lifecycle handbook"
```

---

### Task 4: handbook/review-protocol.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/handbook/review-protocol.md`

**Step 1: 创建文件**

````markdown
# Review 协议

## Reviewer 边界

Reviewer Agent **只能写**到：

- `docs/agentrace/reviews/`
- `docs/agentrace/inbox/`
- `docs/agentrace/decisions/`（触发架构决策时）

**不能**：

- 改 `src/` 等代码目录
- 改 `stories/<id>.md` 的 `status:` 字段
- 改任何 commit

边界由 `bin/agentrace check` 校验：commit author ≠ Story.assignee 且触及 `status:` 字段时告警"疑似 Reviewer 越权"。

## Verdict 类型

| verdict | 含义 | Story 状态机反应 |
|---------|------|------------------|
| `approved` | 通过，可推进 done | author 调 `advance <id> done` |
| `changes_requested` | 必须返工 | 自动 `advance <id> in_progress` |
| `needs_discussion` | 阻塞，需决策 | Story → blocked，Reviewer 创建 D-NNN |

## 多轮 Review

第 N 轮 review 文件名 `R-NNN-on-S-MMM.md`，frontmatter：

```yaml
---
id: R-NNN
story: S-MMM
iteration: N
addresses_reviews: [R-prev-id]
based_on_commits: [new-commits-only]
verdict: ...
---
```

历史 review 不删除，作为审计记录。

## 何时创建 Decision

Review 中遇到架构 / 接口 / 库选择类问题：

1. 自动创建 `docs/agentrace/decisions/D-NNN-<slug>.md`
2. 在 review body 的"关联"段引用 D-NNN
3. 决策落地后（Decision 状态变 `accepted`），Reviewer 把 review verdict 改为 `approved`

## Review body 必填章节

```
## 总结
## Blocker（必须修复）
## 非 Blocker（建议改进，不阻塞）
## 提问 / 讨论
## 关联
```

`## Blocker` 可为空（表示无 Blocker），但章节必须存在。
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/handbook/review-protocol.md
git commit -m "docs: add review protocol handbook"
```

---

### Task 5: handbook/conventions.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/handbook/conventions.md`

**Step 1: 创建文件**

````markdown
# 命名与格式约定

## ID 体系

- Story: `S-NNN`（3 位补零，全局递增）
- Review: `R-NNN-on-S-MMM`
- Decision: `D-NNN`
- Inbox: `I-NNN`（可选，也可不用 ID）

ID 由 `bin/agentrace new-*` 自动分配，禁止手写。

## 文件名

`<ID>-<slug>.md`，slug 是小写连字符英文：

- `S-001-basic-arithmetic.md`
- `R-001-on-S-001.md`
- `D-001-use-dataclass.md`

slug 不必与 title 完全一致，但要能识别主题。

## commit message

```
<type>: <description> (S-NNN)
```

- type: feat / fix / refactor / docs / test / chore
- 必含一个 Story ID
- 多 Story 关联：`feat: x (S-001, S-003)`

`bin/agentrace sync` 从 git log 提取并更新 `Story.related_commits`。

## 章节约定

Story body 章节顺序固定：

```
## 背景
## 范围
## 验收标准
## 技术备注
## 实现日志（changelog，不要手编辑）
```

Review body：

```
## 总结
## Blocker（必须修复）
## 非 Blocker（建议）
## 提问 / 讨论
## 关联
```

Decision body（ADR 风格）：

```
## 状态（proposed / accepted / deprecated）
## 上下文
## 决策
## 影响
```

## YAML frontmatter 必填字段

| 文件类型 | 必填 |
|---|---|
| Story | id / title / status / author / created / updated |
| Review | id / story / verdict / reviewer / created / based_on_commits |
| Decision | id / title / status / created |

## 日期格式

ISO 8601：`YYYY-MM-DD`
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/handbook/conventions.md
git commit -m "docs: add conventions handbook"
```

---

### Task 5b: handbook/relay-and-triage.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/handbook/relay-and-triage.md`

**Step 1: 创建文件**

````markdown
# 接力与事后现场勘查手册（Relay & Post-Mortem Triage）

## 1. 突发熔断痛点与设计原则

在多 Token Plan（例如 5 小时使用限额）场景下，Agent 进程可能在任意编码时刻因 API 429 报错而突然中断。由于 Agent 无法预知何时发生限额截断，系统**绝不依赖前任 Agent 的主动自知保存**，而是依赖接盘 Agent 的**事后现场勘查（Post-Mortem Triage）**。

## 2. 极速接力工作流

接手项目的 Agent 上线第一步：

```bash
bin/agentrace resume
# 或 bin/agentrace triage
```

该命令自动执行以下分析并输出 20 行极简简报：
1. **Git 差异扫描**：抓取未 commit 的 dirty 文件与暂存区修改。
2. **CodeGraph / AST 拓扑关联**：提取被修改的函数/类符号及其上下游调用方（Callers / Callees）。
3. **单测探针探测**：静默运行关联单测，抓取当前的 Failure / Error 堆栈。
4. **生成行动建议**：明确下一步最小可执行动作，避免盲读海量文件消耗 Token。

## 3. 代码影响面分析（`bin/agentrace impact`）

在修改核心公共接口或提交 Review 前，运行：

```bash
bin/agentrace impact [file_or_symbol]
```

CLI 将结合 AST / CodeGraph 输出影响拓扑，帮助 Agent 和 Reviewer 精准掌握变更波及范围。
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/handbook/relay-and-triage.md
git commit -m "docs: add relay and triage handbook"
```

---

## Phase 2: 协议模板文件

### Task 6: stories/_TEMPLATE.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/stories/_TEMPLATE.md`

**Step 1: 创建文件**

````markdown
---
id: S-NNN
title: <一句话描述>
status: draft
author: <git user.name>
assignee: ""
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
depends_on: []
blocks: []
related_reviews: []
related_commits: []
tags: []
priority: P1
blocked_by: ""
---

## 背景

为什么要做。引用 D-001 (决策) 或 inbox 条目。

## 范围

- 做什么
- **不**做什么（防止 scope creep）

## 验收标准

- [ ] 可独立验证的条件 1
- [ ] 可独立验证的条件 2
- [ ] 测试覆盖率 ≥ 80%（适用时）

## 技术备注

架构选择、依赖、已知坑。

## 实现日志（changelog）

<!-- bin/agentrace advance 会自动追加；不要手编辑本节 -->

- <YYYY-MM-DD HH:MM>  status: draft → planned
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/stories/_TEMPLATE.md
git commit -m "docs: add Story template"
```

---

### Task 7: reviews/_TEMPLATE.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/reviews/_TEMPLATE.md`

**Step 1: 创建文件**

````markdown
---
id: R-NNN
story: S-MMM
reviewer: <git user.name>
created: <YYYY-MM-DD>
based_on_commits: []
iteration: 1
verdict: needs_discussion
addresses_reviews: []
---

## 总结

2-3 句总体评价，引用关键 commit / 设计选择。

## Blocker（必须修复）

<!-- 每个 Blocker 含：文件:行号 + 问题描述 + 修复建议 -->

- `<file>:<line>` — 问题描述
  - 建议: 修复方案

## 非 Blocker（建议改进）

- `<file>:<line>` — 改进建议

## 提问 / 讨论

- 待澄清的问题

## 关联

- 涉及决策: D-NNN
- 涉及 inbox: I-NNN
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/reviews/_TEMPLATE.md
git commit -m "docs: add Review template"
```

---

### Task 8: inbox/README.md + decisions/D-001

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/inbox/README.md`
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/decisions/D-001-use-yaml-frontmatter.md`

**Step 1: 创建 `inbox/README.md`**

````markdown
# Inbox

跨 Agent 的临时便条。**不阻塞** Story，但被 `bin/agentrace check` 跟踪。

## 何时写

- 上一个 Agent 跑完发现的下个 Agent 可能踩的坑
- Reviewer 提问但作者暂时没回
- "这件事以后要做"的备忘
- 跨项目的想法

## 何时处理

每周或在 Story 推进时扫一次：

- 可执行 → 转成 Story（`bin/agentrace new-story`，inbox 条目链接过去）
- 不可执行 → 留在这里，加 `#hold` 或 `#wontfix` 标签
- 已解决 → 删除或归档到 `inbox/archive/`

## 文件命名

- `I-NNN-<slug>.md`（有 ID）
- 或 `<YYYY-MM-DD>-<slug>.md`（无 ID，便条性质）

## frontmatter

```yaml
---
id: I-003                    # 可选
created: 2026-08-17
from: claude-impl-A          # 谁留的
tags: [follow-up, perf]
status: open                 # open / hold / wontfix / done
---
```

## 模板

```
## 问题

<描述>

## 建议下一步

- 转成 Story：bin/agentrace new-story
- 或加 #hold / #wontfix
```
````

**Step 2: 创建 `decisions/D-001-use-yaml-frontmatter.md`**

````markdown
---
id: D-001
title: 使用 YAML frontmatter 而非 JSON 或 TOML
status: accepted
created: 2026-08-10
---

## 状态

accepted (2026-08-10)

## 上下文

markdown 文件需要存元数据（id、status、created 等）。
候选方案：

1. YAML frontmatter（GitHub 渲染友好，解析库多）
2. JSON frontmatter（严格但丑）
3. TOML frontmatter（Python 友好但工具支持弱）
4. 完全无 frontmatter，元数据靠文件名推断（脆弱）

## 决策

采用 **YAML frontmatter**（方案 1）。

理由：

- GitHub / VSCode / Antigravity 全部原生渲染
- Python `pyyaml` 已是事实标准
- 注释语法 `#` 方便 inline 注解
- 与现有 ADR 工具（adr-tools）生态兼容

## 影响

- 所有 .md 文件必有 frontmatter
- `bin/agentrace check` 校验必填字段
- 文件名 slug 仅作可读性，元数据以 frontmatter 为准
````

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/inbox/ docs/agentrace/decisions/
git commit -m "docs: add inbox README and D-001 use-yaml-frontmatter"
```

---

### Task 9: plan/ROADMAP.md 模板

**Files:**
- Create: `/Users/jason/python/AI/agentrace/docs/agentrace/plan/ROADMAP.md`

**Step 1: 创建文件**

````markdown
# agentrace 路线图

本季度目标：把 agentrace v0.1 从设计稿变成可运行的模板。

## 已完成

- [x] 设计 spec（2026-08-17）
- [x] AGENTS.md / CLAUDE.md / GEMINI.md
- [x] handbook 三件（story-lifecycle / review-protocol / conventions）

## 进行中

- [ ] bin/agentrace CLI 实现
- [ ] examples/calculator 完整数据
- [ ] 适配器片段 + install-snippet

## 计划中

- [ ] 自检：bin/agentrace check --strict 全通过
- [ ] 发布到 PyPI（可选）

## 阻塞

（暂无）

## 季度外

- 性能基准测试
- 类型注解覆盖率提升到 100%
- 国际化（i18n）

---

> 更新方式：完成 Story 后跑 `bin/agentrace sync`，本文件手动维护季度目标。
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add docs/agentrace/plan/ROADMAP.md
git commit -m "docs: add ROADMAP.md template"
```

---

## Phase 3: 示例项目 calculator

### Task 10: calculator 骨架

**Files:**
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/pyproject.toml`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/src/calculator/__init__.py`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/src/calculator/core.py`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/tests/__init__.py`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/tests/test_core.py`

**Step 1: 创建 `pyproject.toml`**

```toml
[project]
name = "calculator"
version = "0.1.0"
description = "agentrace protocol demo: mini calculator library"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: 创建 `src/calculator/__init__.py`**

```python
"""agentrace demo: mini calculator."""
from .core import CalculatorError, Result, add, sub, mul, div, pow

__all__ = ["CalculatorError", "Result", "add", "sub", "mul", "div", "pow"]
__version__ = "0.1.0"
```

**Step 3: 创建初始 `src/calculator/core.py`（含占位 raise NotImplementedError）**

```python
"""核心计算逻辑。"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    value: float
    op: str


class CalculatorError(ValueError):
    """所有领域错误的基类。"""


def add(a: float, b: float) -> Result:
    raise NotImplementedError


def sub(a: float, b: float) -> Result:
    raise NotImplementedError


def mul(a: float, b: float) -> Result:
    raise NotImplementedError


def div(a: float, b: float) -> Result:
    raise NotImplementedError


def pow(a: float, b: int) -> Result:
    raise NotImplementedError
```

**Step 4: 创建 `tests/__init__.py`**

```python
# tests 包初始化文件
```

**Step 5: 创建初始 `tests/test_core.py`（先全部 skip 或 expected fail）**

```python
import pytest
from calculator import add, sub, mul, div, pow, CalculatorError


def test_add():
    assert add(1, 2).value == 3


def test_sub():
    assert sub(5, 3).value == 2


def test_mul():
    assert mul(3, 4).value == 12


def test_div():
    assert div(10, 2).value == 5


def test_div_by_zero():
    with pytest.raises(CalculatorError):
        div(1, 0)


def test_pow():
    assert pow(2, 10).value == 1024


def test_pow_negative_exponent():
    with pytest.raises(CalculatorError):
        pow(2, -1)
```

**Step 6: 验证测试框架可跑（应全部失败但 pytest 能运行）**

Run: `cd /Users/jason/python/AI/agentrace/examples/calculator && pip install -e . && pytest -v`
Expected: pytest 启动，所有 test_xxx 失败（NotImplementedError），但 pytest 本身正常

**Step 7: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/
git commit -m "feat(calculator): scaffold with skeleton + failing tests"
```

---

### Task 11: 实现 add/sub/mul/div（S-001）

**Files:**
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/src/calculator/core.py`

**Step 1: 替换 `core.py` 中的四则运算**

把第 18-32 行：

```python
def add(a: float, b: float) -> Result:
    raise NotImplementedError


def sub(a: float, b: float) -> Result:
    raise NotImplementedError


def mul(a: float, b: float) -> Result:
    raise NotImplementedError


def div(a: float, b: float) -> Result:
    raise NotImplementedError
```

替换为：

```python
def add(a: float, b: float) -> Result:
    return Result(float(a + b), "add")


def sub(a: float, b: float) -> Result:
    return Result(float(a - b), "sub")


def mul(a: float, b: float) -> Result:
    return Result(float(a * b), "mul")


def div(a: float, b: float) -> Result:
    if b == 0:
        raise CalculatorError("division by zero")
    return Result(float(a / b), "div")
```

**Step 2: 跑测试验证 add/sub/mul/div 通过（pow 仍失败）**

Run: `cd /Users/jason/python/AI/agentrace/examples/calculator && pytest -v`
Expected: 6 个 test_add/sub/mul/div 测试通过，test_div_by_zero 通过；test_pow / test_pow_negative_exponent 仍失败

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/src/calculator/core.py
git commit -m "feat(calculator): implement add/sub/mul/div with zero-division guard (S-001)"
```

---

### Task 12: 实现 pow + 错误处理细化（S-002）

**Files:**
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/src/calculator/core.py`

**Step 1: 把单一 `CalculatorError` 拆分为具体子类**

在 `CalculatorError` 后插入：

```python
class ZeroDivisionError_(CalculatorError):
    """除零错误。"""


class NegativeExponentError(CalculatorError):
    """负指数不支持。"""
```

并把 `div` 函数中的 `raise CalculatorError("division by zero")` 改为 `raise ZeroDivisionError_("division by zero")`。

**Step 2: 实现 pow**

替换 `pow` 函数：

```python
def pow(a: float, b: int) -> Result:
    if b < 0:
        raise NegativeExponentError("negative exponent not supported")
    return Result(float(a ** b), "pow")
```

**Step 3: 更新 `__init__.py` 导出新错误类**

替换 `/Users/jason/python/AI/agentrace/examples/calculator/src/calculator/__init__.py`：

```python
"""agentrace demo: mini calculator."""
from .core import (
    CalculatorError,
    NegativeExponentError,
    Result,
    ZeroDivisionError_,
    add,
    div,
    mul,
    pow,
    sub,
)

__all__ = [
    "CalculatorError",
    "NegativeExponentError",
    "Result",
    "ZeroDivisionError_",
    "add",
    "div",
    "mul",
    "pow",
    "sub",
]
__version__ = "0.1.0"
```

**Step 4: 更新测试以验证具体错误类**

替换 `/Users/jason/python/AI/agentrace/examples/calculator/tests/test_core.py`：

```python
import pytest
from calculator import (
    CalculatorError,
    NegativeExponentError,
    Result,
    ZeroDivisionError_,
    add,
    div,
    mul,
    pow,
    sub,
)


def test_add_returns_result_dataclass():
    r = add(1, 2)
    assert isinstance(r, Result)
    assert r.value == 3
    assert r.op == "add"


def test_sub():
    assert sub(5, 3).value == 2


def test_mul():
    assert mul(3, 4).value == 12


def test_div():
    assert div(10, 2).value == 5


def test_div_by_zero_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError_):
        div(1, 0)


def test_pow_positive_exponent():
    assert pow(2, 10).value == 1024


def test_pow_zero_exponent():
    assert pow(5, 0).value == 1


def test_pow_negative_exponent_raises():
    with pytest.raises(NegativeExponentError):
        pow(2, -1)
```

**Step 5: 跑全测试**

Run: `cd /Users/jason/python/AI/agentrace/examples/calculator && pytest -v`
Expected: 全部 8 个 test 通过

**Step 6: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/
git commit -m "feat(calculator): implement pow with error class split (S-002)"
```

---

### Task 13: calculator README + Decision D-001

**Files:**
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/README.md`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/decisions/D-001-use-dataclass.md`

**Step 1: 创建 calculator/README.md**

````markdown
# Calculator 示例

一个 60 行的 mini Python 库，演示 agentrace的完整状态机路径。

## 怎么读这个示例

1. 从 `docs/agentrace/stories/` 开始，按 S-001 → S-002 → S-003 → S-004 顺序读
2. 对照 `docs/agentrace/reviews/` 看每一轮的反馈
3. 跑 `bin/agentrace check --strict` 验证示例数据完整
4. 对比 `src/calculator/core.py` 和 S-002 的实现日志，看返工流如何留痕

## 涵盖的状态机路径

| Story | 路径 | 演示点 |
|-------|------|--------|
| S-001 | draft → planned → in_progress → in_review → done | 一次性通过 |
| S-002 | ... → in_review → in_progress → in_review → done | 两轮 review + 返工 |
| S-003 | draft → planned | 长期 planned，验收标准留 TODO |
| S-004 | draft → planned → blocked | 卡在架构决策 |

## 运行

```bash
pip install -e .
pytest -v
```

## API

```python
from calculator import add, sub, mul, div, pow

add(1, 2).value       # 3
sub(5, 3).value       # 2
mul(3, 4).value       # 12
div(10, 2).value      # 5
pow(2, 10).value      # 1024

div(1, 0)             # raises ZeroDivisionError_
pow(2, -1)            # raises NegativeExponentError
```
````

**Step 2: 创建 Decision 文件**

````markdown
---
id: D-001
title: 使用 dataclass 表达 Result 而非 dict
status: accepted
created: 2026-08-10
---

## 状态

accepted (2026-08-10)

## 上下文

S-001 需要为四则运算返回结果。候选：

1. `dict`：轻，但无类型提示
2. `dataclass`：类型安全 + frozen 保证不可变
3. `tuple`：最快但语义弱
4. `pydantic.BaseModel`：重，引入外部依赖

## 决策

采用 **dataclass(frozen=True)**（方案 2）。

理由：

- 不可变（frozen）保证函数式风格
- IDE / mypy / pyright 全部支持
- 零额外依赖
- 与 S-002 错误处理（也用 dataclass 化的 Error 层级）风格一致

## 影响

- Result 类型 `{ value: float, op: str }`
- 错误类继承 `CalculatorError`，具体子类 `ZeroDivisionError_` / `NegativeExponentError`
- 测试用 `isinstance(r, Result)` 验证
````

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/README.md examples/calculator/docs/agentrace/decisions/
git commit -m "docs(calculator): add README and D-001 use-dataclass"
```

---

## Phase 4: 示例项目 docs/agentrace/

### Task 14: S-001 + R-001（一次性通过示例）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/stories/S-001-basic-arithmetic.md`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/reviews/R-001-on-S-001.md`

**Step 1: 创建 S-001**

````markdown
---
id: S-001
title: 实现基础四则运算 add/sub/mul/div
status: done
author: claude-impl-A
assignee: claude-impl-A
created: 2026-08-10
updated: 2026-08-12
depends_on: []
blocks: []
related_reviews: [R-001]
related_commits: ["<filled-by-bin-agents-sync>"]
tags: [core]
priority: P1
blocked_by: ""
---

## 背景

calculator 库的第一个 Story。四则运算是任何计算器的基础。

## 范围

- 实现 `add` / `sub` / `mul` / `div`
- div 处理除零错误
- 不含 power（走 S-002）

## 验收标准

- [x] 4 个函数全部实现，返回 `Result` dataclass
- [x] `div(1, 0)` 抛 `CalculatorError`
- [x] pytest 全部通过
- [x] 测试覆盖率 ≥ 90%

## 技术备注

- `Result` 用 `dataclass(frozen=True)`（见 D-001）
- 错误类型先用单一 `CalculatorError`，细化推迟到 S-002
- 输入统一转 `float` 保证类型一致

## 实现日志

- 2026-08-10  status: draft → planned
- 2026-08-11  status: planned → in_progress (assignee=claude-impl-A)
- 2026-08-11  commit: add/sub/mul/div skeleton with NotImplementedError
- 2026-08-11  commit: implement add/sub/mul/div + div-by-zero guard
- 2026-08-12  status: in_progress → in_review
- 2026-08-12  approved by R-001
- 2026-08-12  status: in_review → done
````

**Step 2: 创建 R-001**

````markdown
---
id: R-001
story: S-001
reviewer: antigravity-review-A
created: 2026-08-12
based_on_commits: ["<filled-by-bin-agents-sync>"]
iteration: 1
verdict: approved
addresses_reviews: []
---

## 总结

实现干净，测试覆盖到位。3 处小建议在 "非 Blocker"。

## Blocker（必须修复）

无

## 非 Blocker（建议）

- `src/calculator/core.py:15` — `add` 没考虑 NaN 输入；可选
- `tests/test_core.py:30` — 浮点比较建议用 `pytest.approx`
- `src/calculator/core.py:30` — `div` 返回 `float` 时可考虑保留更多小数位

## 提问 / 讨论

无

## 关联

- 涉及决策: D-001 (使用 dataclass)
````

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/docs/agentrace/stories/S-001-basic-arithmetic.md examples/calculator/docs/agentrace/reviews/R-001-on-S-001.md
git commit -m "docs(calculator): add S-001 + R-001 (one-pass review example)"
```

---

### Task 15: S-002 + R-002（changes_requested 返工示例）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/stories/S-002-power-and-errors.md`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/reviews/R-002-on-S-002.md`

**Step 1: 创建 S-002**

````markdown
---
id: S-002
title: 实现 power + 细化错误处理
status: in_review
author: claude-impl-A
assignee: claude-impl-A
created: 2026-08-13
updated: 2026-08-15
depends_on: [S-001]
blocks: []
related_reviews: [R-002]
related_commits: ["<filled-by-bin-agents-sync>"]
tags: [core, errors]
priority: P1
blocked_by: ""
---

## 背景

S-001 完成了基础四则运算。本 Story 补全 power 运算，并把单一 `CalculatorError` 拆分为具体子类，便于上层精确捕获。

## 范围

- 实现 `pow(a, b: int)` 函数
- 拆 `CalculatorError` 为 `ZeroDivisionError_` / `NegativeExponentError`
- 不含缓存 / 链式调用（走 S-004）

## 验收标准

- [x] `pow(2, 10).value == 1024`
- [x] `pow(5, 0).value == 1`
- [x] `pow(2, -1)` 抛 `NegativeExponentError`
- [x] `div(1, 0)` 抛 `ZeroDivisionError_`（不再是 `CalculatorError`）
- [x] pytest 全部通过，覆盖率 ≥ 90%
- [ ] R-002 提到的 Blocker 全部修复

## 技术备注

- power 只支持非负整数指数，负指数抛错（不引入分数运算复杂度）
- 错误类用 `CalculatorError` 基类 + 子类模式，方便 `except CalculatorError` 兜底
- 名字加下划线避免与 builtin `ZeroDivisionError` 冲突

## 实现日志

- 2026-08-13  status: draft → planned
- 2026-08-13  status: planned → in_progress
- 2026-08-13  commit: implement pow + split error classes
- 2026-08-14  status: in_progress → in_review
- 2026-08-14  changes_requested by R-002
                  - 缺 pow(a, 0) 边界 case
                  - 错误类型用 CalculatorError 太粗
- 2026-08-15  status: in_review → in_progress (返工)
- 2026-08-15  commit: add pow(a, 0) case + split ZeroDivisionError_/NegativeExponentError
- 2026-08-15  status: in_progress → in_review
                  @antigravity 请 re-review
````

**Step 2: 创建 R-002**

````markdown
---
id: R-002
story: S-002
reviewer: antigravity-review-A
created: 2026-08-14
based_on_commits: ["<filled-by-bin-agents-sync>"]
iteration: 1
verdict: changes_requested
addresses_reviews: []
---

## 总结

基本可用，但错误处理粒度不够，边界 case 缺。

## Blocker（必须修复）

- `src/calculator/core.py:35` — `pow(a, 0)` 没单独 case 验证
- `src/calculator/core.py:38` — 单一 `CalculatorError` 太粗，建议拆 `ZeroDivisionError` / `NegativeExponentError`（注意 builtin `ZeroDivisionError` 名字冲突，可加下划线或前缀）

## 非 Blocker（建议）

- `tests/test_core.py` — 可补充 `@pytest.mark.parametrize` 表格化

## 提问 / 讨论

- 是否支持链式调用 `calc.add(1).add(2)`？影响未来 API 设计，超出本 Story 范围

## 关联

- 涉及决策: D-001
````

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/docs/agentrace/stories/S-002-power-and-errors.md examples/calculator/docs/agentrace/reviews/R-002-on-S-002.md
git commit -m "docs(calculator): add S-002 + R-002 (changes_requested example)"
```

---

### Task 16: R-003-on-S-002（approved follow-up）+ 同步 S-002 状态

**Files:**
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/reviews/R-003-on-S-002.md`
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/stories/S-002-power-and-errors.md`

**Step 1: 把 S-002 状态改为 done，更新 related_reviews**

修改 S-002 frontmatter：
```yaml
status: done
related_reviews: [R-002, R-003]
```

并在实现日志末尾追加：
```
- 2026-08-16  approved by R-003
- 2026-08-16  status: in_review → done
```

**Step 3: 创建 R-003**

````markdown
---
id: R-003
story: S-002
reviewer: antigravity-review-A
created: 2026-08-16
based_on_commits: ["<filled-by-bin-agents-sync>"]
iteration: 2
verdict: approved
addresses_reviews: [R-002]
---

## 总结

所有 Blocker 已修，错误类型拆分符合单一职责。pow(a, 0) case 验证清晰。

## Blocker（必须修复）

无

## 非 Blocker（建议）

- `tests/test_core.py:30` — 可补充 `@pytest.mark.parametrize` 表格化（不阻塞 done）

## 提问 / 讨论

无

## 关联

- addresses: R-002
- 涉及决策: D-001
````

**Step 4: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/docs/agentrace/reviews/R-003-on-S-002.md examples/calculator/docs/agentrace/stories/S-002-power-and-errors.md
git commit -m "docs(calculator): add R-003 follow-up approval, close S-002"
```

---

### Task 17: S-003（planned 长期不动示例）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/stories/S-003-write-readme.md`

**Step 1: 创建 S-003**

````markdown
---
id: S-003
title: 写 calculator README 文档
status: planned
author: claude-impl-A
assignee: ""
created: 2026-08-14
updated: 2026-08-14
depends_on: [S-001]
blocks: []
related_reviews: []
related_commits: []
tags: [docs]
priority: P2
blocked_by: ""
---

## 背景

calculator 包发布到 PyPI 之前需要完整 README：API 用法 + 状态机演示说明。

## 范围

- 在 `examples/calculator/README.md` 加 API 文档章节
- 加 "如何读这个示例" 章节
- 不含教程 / FAQ（季度外）

## 验收标准

<!-- TODO: 接手时填验收标准，然后调 bin/agentrace advance S-003 in_progress -->

## 技术备注

暂无

## 实现日志

- 2026-08-14  status: draft → planned
                  <!-- TODO: 接手时填验收标准 + assignee -->
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/docs/agentrace/stories/S-003-write-readme.md
git commit -m "docs(calculator): add S-003 (planned with TODO)"
```

---

### Task 18: S-004（blocked）+ calculator ROADMAP

**Files:**
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/stories/S-004-cache-last-result.md`
- Create: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/plan/ROADMAP.md`

**Step 1: 创建 S-004**

````markdown
---
id: S-004
title: Calculator 加缓存，记住上次运算
status: blocked
author: claude-impl-A
assignee: ""
created: 2026-08-14
updated: 2026-08-15
depends_on: [S-001]
blocks: []
related_reviews: []
related_commits: []
tags: [perf, caching]
priority: P3
blocked_by: "需 D-002 决策：缓存失效策略（LRU vs TTL vs 永不过期）"
---

## 背景

calculator 库每次调用 `add(1, 2)` 都重算。如果能记住上次结果，省去重复计算。

## 范围

- 在 `Calculator` 类加 `last_result` 字段
- 提供 `cache_clear()` 方法
- 不含线程安全（季度外）

## 验收标准

- [ ] `Calculator().add(1, 2).last_result == Result(3, "add")`
- [ ] `Calculator().cache_clear()` 后 `last_result is None`
- [ ] 缓存策略符合 D-002 决策

## 技术备注

缓存策略依赖架构决策 D-002。

## 实现日志

- 2026-08-14  status: draft → planned
- 2026-08-15  status: planned → blocked
                  @antigravity 请给 D-002 决策（缓存策略）
                  blocked_by: 缓存失效策略未定
````

**Step 2: 创建 ROADMAP.md**

````markdown
# calculator 路线图

本季度目标：完成 calculator v0.1，含基础四则、power、错误处理。

## 已完成

- [x] S-001 基础四则运算
- [x] S-002 power + 错误处理细化

## 进行中

（暂无）

## 计划中

- [ ] S-003 写 README

## 阻塞

- [ ] S-004 缓存上次结果 — blocked 等 D-002

## 季度外

- 链式调用
- 线程安全
- 性能基准
````

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add examples/calculator/docs/agentrace/stories/S-004-cache-last-result.md examples/calculator/docs/agentrace/plan/ROADMAP.md
git commit -m "docs(calculator): add S-004 (blocked) and ROADMAP"
```

---

## Phase 5: bin/agentrace CLI

### Task 19: bin/agentrace 骨架 + 测试基础设施

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/agentrace`
- Create: `/Users/jason/python/AI/agentrace/bin/tests/conftest.py`
- Create: `/Users/jason/python/AI/agentrace/bin/tests/fixtures/sample_project/docs/agentrace/stories/_TEMPLATE.md`
- Create: `/Users/jason/python/AI/agentrace/bin/tests/fixtures/sample_project/docs/agentrace/stories/S-001-test.md`
- Create: `/Users/jason/python/AI/agentrace/bin/tests/__init__.py`

**Step 1: 创建测试基础设施**

`bin/tests/__init__.py`:

```python
# bin/tests 包初始化
```

`bin/tests/conftest.py`:

```python
"""pytest fixtures for bin/agentrace tests."""
import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """复制 fixtures/sample_project 到临时目录，返回路径。"""
    src = FIXTURES / "sample_project"
    dst = tmp_path / "sample_project"
    shutil.copytree(src, dst)
    return dst
```

**Step 2: 创建 sample_project fixtures**

`bin/tests/fixtures/sample_project/docs/agentrace/stories/_TEMPLATE.md`:

````markdown
---
id: S-NNN
title: <title>
status: draft
author: test-author
assignee: ""
created: 2026-01-01
updated: 2026-01-01
depends_on: []
blocks: []
related_reviews: []
related_commits: []
tags: []
priority: P1
blocked_by: ""
---

## 背景

## 范围

## 验收标准

- [ ] 条件 1

## 技术备注

## 实现日志

- 2026-01-01  status: draft
````

`bin/tests/fixtures/sample_project/docs/agentrace/stories/S-001-test.md`:

````markdown
---
id: S-001
title: Test story
status: planned
author: test-author
assignee: ""
created: 2026-01-01
updated: 2026-01-01
depends_on: []
blocks: []
related_reviews: []
related_commits: []
tags: []
priority: P1
blocked_by: ""
---

## 背景

## 范围

## 验收标准

- [ ] 条件 1

## 技术备注

## 实现日志

- 2026-01-01  status: draft → planned
````

**Step 3: 写第一个失败的测试**

`bin/tests/test_new_story.py`:

```python
"""测试 bin/agentrace new-story。"""
from pathlib import Path

import pytest

# 注意：实际命令通过 subprocess 调用 bin/agentrace
# 由于 bin/agentrace 还未实现，先写 stub


def test_new_story_creates_file(sample_project: Path):
    """new-story 应创建 S-NNN-slug.md 文件。"""
    # 这一步在 Task 20 实现
    assert True  # placeholder，等 Task 20 实现后再替换
```

**Step 4: 创建 bin/agentrace 骨架（仅 argparse 入口）**

`bin/agentrace`:

```python
#!/usr/bin/env python3
"""bin/agentrace: agentrace CLI。

命令：
- init: 初始化模板
- install-snippet: 安装用户级片段
- new-story: 创建 Story
- new-review: 创建 Review
- advance: 状态推进
- sync: 同步 AGENTS.md 表格
- check: 校验全集
- render: 生成 OVERVIEW
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def cmd_init(args):
    print("init: not implemented yet")


def cmd_install_snippet(args):
    print("install-snippet: not implemented yet")


def cmd_new_story(args):
    print("new-story: not implemented yet")


def cmd_new_review(args):
    print("new-review: not implemented yet")


def cmd_advance(args):
    print("advance: not implemented yet")


def cmd_sync(args):
    print("sync: not implemented yet")


def cmd_check(args):
    print("check: not implemented yet")


def cmd_render(args):
    print("render: not implemented yet")


def main():
    parser = argparse.ArgumentParser(prog="agentrace", description="agentrace CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init")
    subparsers.add_parser("install-snippet")
    subparsers.add_parser("new-story")
    subparsers.add_parser("new-review")
    p_advance = subparsers.add_parser("advance")
    p_advance.add_argument("story_id")
    p_advance.add_argument("new_status")
    subparsers.add_parser("sync")
    p_check = subparsers.add_parser("check")
    p_check.add_argument("--strict", action="store_true")
    p_check.add_argument("--fix", action="store_true")
    subparsers.add_parser("render")

    args = parser.parse_args()

    handlers = {
        "init": cmd_init,
        "install-snippet": cmd_install_snippet,
        "new-story": cmd_new_story,
        "new-review": cmd_new_review,
        "advance": cmd_advance,
        "sync": cmd_sync,
        "check": cmd_check,
        "render": cmd_render,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
```

**Step 5: 给 bin/agentrace 加执行权限 + 验证骨架可调用**

```bash
chmod +x /Users/jason/python/AI/agentrace/bin/agentrace
/Users/jason/python/AI/agentrace/bin/agentrace --help
```

Expected: 打印 usage，含 init / install-snippet / new-story / new-review / advance / sync / check / render

**Step 6: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): scaffold CLI with argparse + test fixtures"
```

---

### Task 20: bin/agentrace new-story（TDD）

**Files:**
- Modify: `/Users/jason/python/AI/agentrace/bin/tests/test_new_story.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败的测试**

替换 `bin/tests/test_new_story.py`:

```python
"""测试 bin/agentrace new-story。"""
import subprocess
from pathlib import Path

import pytest

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_new_story_creates_file(sample_project: Path):
    """new-story 应创建 S-002-new-feature.md 文件。"""
    result = run_agents(sample_project, "new-story", "--title", "新功能")
    assert result.returncode == 0, result.stderr
    created = sample_project / "docs/agentrace/stories/S-002-new-feature.md"
    assert created.exists()


def test_new_story_assigns_next_id(sample_project: Path):
    """new-story 应在现有 S-001 基础上分配 S-002。"""
    result = run_agents(sample_project, "new-story", "--title", "另一个")
    assert result.returncode == 0
    files = list((sample_project / "docs/agentrace/stories").glob("S-*.md"))
    assert any(f.name.startswith("S-002") for f in files)


def test_new_story_fills_frontmatter(sample_project: Path):
    """新 Story 应填好 frontmatter 各字段。"""
    run_agents(sample_project, "new-story", "--title", "测试 story")
    content = (sample_project / "docs/agentrace/stories/S-002-test-story.md").read_text()
    assert "id: S-002" in content
    assert "status: draft" in content
    assert "title: 测试 story" in content
    assert "## 背景" in content
    assert "## 实现日志" in content
```

**Step 2: 跑测试，验证全部失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_new_story.py -v`
Expected: 3 个 test 全部失败（"not implemented yet"）

**Step 3: 实现 new-story 命令**

替换 `cmd_new_story` 函数：

```python
import datetime
import re
from typing import Optional


def _next_story_id(stories_dir: Path) -> int:
    """扫 stories/ 返回 max ID + 1。"""
    max_id = 0
    for f in stories_dir.glob("S-*.md"):
        m = re.match(r"S-(\d+)", f.name)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return max_id + 1


def _slugify(title: str) -> str:
    """转 title 为文件 slug。中文转拼音留待 v0.2；这里只用 ascii 化简版。"""
    s = title.lower().strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    return s or "untitled"


def cmd_new_story(args):
    stories_dir = Path.cwd() / "docs/agentrace/stories"
    if not stories_dir.exists():
        print(f"error: {stories_dir} 不存在，请先 bin/agentrace init", file=sys.stderr)
        sys.exit(1)

    template = stories_dir / "_TEMPLATE.md"
    if not template.exists():
        print(f"error: {template} 缺失", file=sys.stderr)
        sys.exit(1)

    next_id = _next_story_id(stories_dir)
    title = args.title or "Untitled story"
    slug = _slugify(title)
    today = datetime.date.today().isoformat()

    content = template.read_text()
    content = content.replace("S-NNN", f"S-{next_id:03d}")
    content = content.replace("<title>", title)
    content = content.replace("<YYYY-MM-DD>", today)
    content = re.sub(r"author: [^\n]*", "author: test-author", content)

    target = stories_dir / f"S-{next_id:03d}-{slug}.md"
    target.write_text(content)
    print(f"created: {target.relative_to(Path.cwd())}")
```

并在 argparse 部分替换：

```python
p_new_story = subparsers.add_parser("new-story")
p_new_story.add_argument("--title", default="")
```

并把 `argparse` 模块的 `add_parser("new-story")` 那行删掉（已被替换）。

**Step 4: 跑测试，验证通过**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_new_story.py -v`
Expected: 3 个 test 全部通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement new-story with TDD"
```

---

### Task 21: bin/agentrace new-review（TDD）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_new_review.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_new_review.py`:

```python
"""测试 bin/agentrace new-review。"""
import subprocess
from pathlib import Path

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_new_review_creates_file(sample_project: Path):
    """new-review S-001 应创建 R-001-on-S-001.md。"""
    result = run_agents(sample_project, "new-review", "S-001")
    assert result.returncode == 0, result.stderr
    created = sample_project / "docs/agentrace/reviews/R-001-on-S-001.md"
    assert created.exists()


def test_new_review_fills_frontmatter(sample_project: Path):
    """新 Review 应填好 story、verdict=needs_discussion、iteration=1。"""
    run_agents(sample_project, "new-review", "S-001")
    content = (sample_project / "docs/agentrace/reviews/R-001-on-S-001.md").read_text()
    assert "story: S-001" in content
    assert "verdict: needs_discussion" in content
    assert "iteration: 1" in content


def test_new_review_requires_existing_story(sample_project: Path):
    """new-review S-999（不存在）应失败。"""
    result = run_agents(sample_project, "new-review", "S-999")
    assert result.returncode != 0
    assert "S-999" in result.stderr or "not found" in result.stderr.lower()
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_new_review.py -v`
Expected: 3 个 test 失败

**Step 3: 实现 new-review**

替换 `cmd_new_review` 函数：

```python
def _next_review_id(reviews_dir: Path) -> int:
    max_id = 0
    for f in reviews_dir.glob("R-*.md"):
        m = re.match(r"R-(\d+)", f.name)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return max_id + 1


def cmd_new_review(args):
    story_id = args.story_id
    stories_dir = Path.cwd() / "docs/agentrace/stories"
    reviews_dir = Path.cwd() / "docs/agentrace/reviews"

    story_file = stories_dir / f"{story_id}.md"
    # 允许带 slug 的文件名
    matches = list(stories_dir.glob(f"{story_id}-*.md"))
    if not story_file.exists() and not matches:
        print(f"error: story {story_id} not found in {stories_dir}", file=sys.stderr)
        sys.exit(1)

    template = reviews_dir / "_TEMPLATE.md"
    if not template.exists():
        print(f"error: {template} 缺失", file=sys.stderr)
        sys.exit(1)

    next_id = _next_review_id(reviews_dir)
    today = datetime.date.today().isoformat()

    content = template.read_text()
    content = content.replace("R-NNN", f"R-{next_id:03d}")
    content = content.replace("S-MMM", story_id)
    content = content.replace("<YYYY-MM-DD>", today)

    target = reviews_dir / f"R-{next_id:03d}-on-{story_id}.md"
    target.write_text(content)
    print(f"created: {target.relative_to(Path.cwd())}")
```

并替换 argparse：

```python
p_new_review = subparsers.add_parser("new-review")
p_new_review.add_argument("story_id")
```

（删除旧 `subparsers.add_parser("new-review")`）

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_new_review.py -v`
Expected: 3 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement new-review with TDD"
```

---

### Task 22: bin/agentrace advance（核心状态机）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_advance.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_advance.py`:

```python
"""测试 bin/agentrace advance（核心状态机）。"""
import subprocess
from pathlib import Path

import pytest

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_advance_draft_to_planned(sample_project: Path):
    """draft → planned：当前 S-001 已 planned，所以测新建一个 draft。"""
    run_agents(sample_project, "new-story", "--title", "draft test")
    # 新创建的 Story 是 draft 状态
    result = run_agents(sample_project, "advance", "S-002", "planned")
    assert result.returncode == 0, result.stderr
    content = (sample_project / "docs/agentrace/stories/S-002-draft-test.md").read_text()
    assert "status: planned" in content


def test_advance_requires_assignee(sample_project: Path):
    """planned → in_progress 必须有 assignee。"""
    # S-001 是 planned 但 assignee 为空
    result = run_agents(sample_project, "advance", "S-001", "in_progress")
    assert result.returncode != 0
    assert "assignee" in result.stderr.lower()


def test_advance_planned_to_in_progress(sample_project: Path):
    """填 assignee 后 planned → in_progress 应成功。"""
    story = sample_project / "docs/agentrace/stories/S-001-test.md"
    content = story.read_text()
    content = content.replace("assignee: \"\"", "assignee: \"claude-impl-A\"")
    story.write_text(content)

    result = run_agents(sample_project, "advance", "S-001", "in_progress")
    assert result.returncode == 0, result.stderr
    new_content = story.read_text()
    assert "status: in_progress" in new_content
    # changelog 追加
    assert "planned → in_progress" in new_content


def test_advance_invalid_transition_rejected(sample_project: Path):
    """draft → done 应被拒绝（不允许跳级）。"""
    # 新 Story 默认 draft
    run_agents(sample_project, "new-story", "--title", "invalid test")
    result = run_agents(sample_project, "advance", "S-002", "done")
    assert result.returncode != 0
    assert "transition" in result.stderr.lower() or "invalid" in result.stderr.lower()
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_advance.py -v`
Expected: 4 个 test 失败

**Step 3: 实现 advance**

替换 `cmd_advance` 函数：

```python
VALID_TRANSITIONS = {
    ("draft", "planned"),
    ("planned", "in_progress"),
    ("in_progress", "in_review"),
    ("in_progress", "blocked"),
    ("in_review", "done"),
    ("in_review", "in_progress"),
    ("in_review", "blocked"),
    ("planned", "blocked"),
    ("draft", "blocked"),
    ("blocked", "planned"),
    ("blocked", "in_progress"),
    ("blocked", "in_review"),
}


def _parse_frontmatter(path: Path) -> dict:
    """读 .md frontmatter + body。"""
    import yaml
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def _write_frontmatter(path: Path, fm: dict, body: str):
    """写回 frontmatter + body。"""
    import yaml
    text = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n" + body
    path.write_text(text)


def cmd_advance(args):
    story_id = args.story_id
    new_status = args.new_status

    stories_dir = Path.cwd() / "docs/agentrace/stories"
    matches = list(stories_dir.glob(f"{story_id}-*.md"))
    if not matches:
        print(f"error: story {story_id} not found", file=sys.stderr)
        sys.exit(1)
    story_file = matches[0]

    text = story_file.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        print(f"error: {story_file} frontmatter 格式错误", file=sys.stderr)
        sys.exit(1)

    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    current = fm.get("status")

    # 校验转换合法
    if (current, new_status) not in VALID_TRANSITIONS:
        print(f"error: invalid transition {current} → {new_status}", file=sys.stderr)
        sys.exit(1)

    # 校验附加条件
    if new_status == "in_progress" and not fm.get("assignee"):
        print(f"error: planned → in_progress requires assignee", file=sys.stderr)
        sys.exit(1)

    if new_status == "in_review" and not fm.get("related_commits"):
        print(f"warning: in_progress → in_review but related_commits 为空", file=sys.stderr)

    # 改 status + 追加 changelog
    old_status = current
    fm["status"] = new_status
    fm["updated"] = datetime.date.today().isoformat()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    changelog_line = f"- {timestamp}  status: {old_status} → {new_status}"
    body = body.rstrip() + "\n" + changelog_line + "\n"

    _write_frontmatter(story_file, fm, body)
    print(f"advanced: {story_id} {old_status} → {new_status}")
```

确认 `bin/agentrace` 顶部 import 包含 `yaml`：

```python
from __future__ import annotations
import argparse
import datetime
import re
import sys
from pathlib import Path

import yaml
```

（不需要 `python-frontmatter` 库——直接手写 `---` 分割更可控。）

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_advance.py -v`
Expected: 4 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement advance with state machine enforcement (TDD)"
```

---

### Task 23: bin/agentrace sync

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_sync.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_sync.py`:

```python
"""测试 bin/agentrace sync。"""
import subprocess
from pathlib import Path

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_sync_updates_agents_md_table(sample_project: Path):
    """sync 应在 AGENTS.md 的"当前激活 Story"表中反映所有 Story。"""
    # 准备：sample_project 没有 AGENTS.md，先放一个 minimal 的
    agents_md = sample_project / "AGENTS.md"
    agents_md.write_text("# AGENTS\n\n## 当前激活 Story\n\n<!-- bin/agentrace sync -->\n\n## 路线图\n")

    run_agents(sample_project, "sync")
    content = agents_md.read_text()
    assert "S-001" in content
    assert "Test story" in content or "test" in content.lower()
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_sync.py -v`
Expected: 1 个 test 失败

**Step 3: 实现 sync**

替换 `cmd_sync` 函数：

```python
SYMBOLS_CACHE = ".agents/symbols-cache.yaml"


def cmd_sync(args):
    cwd = Path.cwd()
    agents_md = cwd / "AGENTS.md"
    stories_dir = cwd / "docs/agentrace/stories"

    if not stories_dir.exists():
        print("error: docs/agentrace/stories/ 不存在", file=sys.stderr)
        sys.exit(1)

    # 读符号缓存（resume / impact 命令会写这里）
    cache_path = cwd / SYMBOLS_CACHE
    symbols_cache: dict[str, list[str]] = {}
    if cache_path.exists():
        symbols_cache = yaml.safe_load(cache_path.read_text()) or {}

    # 扫所有 Story
    stories = []
    for f in sorted(stories_dir.glob("S-*.md")):
        text = f.read_text()
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1]) or {}
        body = parts[2]

        # 同步 impacted_symbols 字段（spec §6.3）
        sid = fm.get("id", f.stem)
        if sid in symbols_cache:
            fm["impacted_symbols"] = symbols_cache[sid]

        stories.append({
            "id": sid,
            "title": fm.get("title", ""),
            "status": fm.get("status", ""),
            "assignee": fm.get("assignee", "") or "—",
        })

        # 写回 frontmatter（保留 body）
        new_text = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---" + body
        if new_text != text:
            f.write_text(new_text)

    # 生成表格
    table = "| ID | 标题 | 状态 | 负责人 |\n|----|------|------|--------|\n"
    for s in stories:
        table += f"| {s['id']} | {s['title']} | {s['status']} | {s['assignee']} |\n"

    # 替换 AGENTS.md 中 "<!-- bin/agentrace sync -->" 标记之间的内容
    if agents_md.exists():
        text = agents_md.read_text()
        marker = "<!-- bin/agentrace sync -->"
        if marker in text:
            before, _, after = text.partition(marker)
            new_text = before + marker + "\n\n" + table + "\n" + after
            agents_md.write_text(new_text)
            print(f"synced: AGENTS.md updated with {len(stories)} stories")
        else:
            print("warning: AGENTS.md 缺少 <!-- bin/agentrace sync --> 标记", file=sys.stderr)
    else:
        print("warning: AGENTS.md 不存在，跳手同步", file=sys.stderr)
```

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_sync.py -v`
Expected: 1 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement sync to refresh AGENTS.md table (TDD)"
```

---

### Task 24: bin/agentrace check（校验全集）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_check.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_check.py`:

```python
"""测试 bin/agentrace check（校验全集）。"""
import subprocess
from pathlib import Path

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_check_on_valid_project_passes(sample_project: Path):
    """sample_project 应通过 check（默认非 strict）。"""
    result = run_agents(sample_project, "check")
    assert result.returncode == 0, result.stderr


def test_check_missing_required_field_fails(tmp_path: Path):
    """缺必填字段时 check 应报错。"""
    stories_dir = tmp_path / "docs/agentrace/stories"
    stories_dir.mkdir(parents=True)
    (stories_dir / "_TEMPLATE.md").write_text("---\nid: S-NNN\n---\n")
    bad = stories_dir / "S-001-bad.md"
    bad.write_text("---\nid: S-001\nstatus: draft\n---\n## 背景\n")  # 缺 title/author/created/updated

    result = run_agents(tmp_path, "check", "--strict")
    assert result.returncode != 0


def test_check_unique_ids(tmp_path: Path):
    """重复 S-001 应报错。"""
    stories_dir = tmp_path / "docs/agentrace/stories"
    stories_dir.mkdir(parents=True)
    (stories_dir / "_TEMPLATE.md").write_text("---\nid: S-NNN\n---\n")
    for n in ("001-a", "001-b"):
        (stories_dir / f"S-{n}.md").write_text(
            "---\n"
            "id: S-001\n"
            "title: dup\n"
            "status: draft\n"
            "author: x\n"
            "created: 2026-01-01\n"
            "updated: 2026-01-01\n"
            "---\n## 背景\n## 范围\n## 验收标准\n- [ ] x\n## 技术备注\n## 实现日志\n- x\n"
        )

    result = run_agents(tmp_path, "check", "--strict")
    assert result.returncode != 0
    assert "duplicate" in result.stderr.lower() or "重复" in result.stderr
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_check.py -v`
Expected: 3 个 test 失败

**Step 3: 实现 check**

替换 `cmd_check` 函数：

```python
def _parse_md(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def cmd_check(args):
    errors: list[str] = []
    warnings: list[str] = []
    strict = args.strict

    cwd = Path.cwd()
    stories_dir = cwd / "docs/agentrace/stories"
    reviews_dir = cwd / "docs/agentrace/reviews"

    # 1. Story frontmatter 校验
    story_files = sorted(stories_dir.glob("S-*.md")) if stories_dir.exists() else []
    story_ids: set[str] = set()
    for sf in story_files:
        fm, body = _parse_md(sf)
        sid = fm.get("id")
        if not sid:
            errors.append(f"{sf.name}: 缺 id")
            continue

        # 必填字段
        for field in ("title", "status", "author", "created", "updated"):
            if field not in fm:
                errors.append(f"{sf.name}: 缺 {field}")

        # status 枚举
        if fm.get("status") not in {"draft", "planned", "in_progress", "in_review", "blocked", "done", "rejected"}:
            errors.append(f"{sf.name}: status 非法 {fm.get('status')!r}")

        # 唯一性
        if sid in story_ids:
            errors.append(f"{sf.name}: 重复 S ID {sid}")
        story_ids.add(sid)

    # 2. Review frontmatter + 引用闭合
    review_files = sorted(reviews_dir.glob("R-*.md")) if reviews_dir.exists() else []
    review_ids: set[str] = set()
    for rf in review_files:
        fm, _ = _parse_md(rf)
        rid = fm.get("id")
        story_ref = fm.get("story")
        verdict = fm.get("verdict")

        if not rid:
            errors.append(f"{rf.name}: 缺 id")
        else:
            if rid in review_ids:
                errors.append(f"{rf.name}: 重复 R ID {rid}")
            review_ids.add(rid)

        if story_ref and story_ref not in story_ids:
            errors.append(f"{rf.name}: 引用不存在的 story {story_ref}")

        if verdict not in {"approved", "changes_requested", "needs_discussion", None}:
            errors.append(f"{rf.name}: verdict 非法 {verdict!r}")

        # Blocker 或 总结 章节
        if "## Blocker" not in (_ or "") and "## 总结" not in (_):
            warnings.append(f"{rf.name}: 缺 ## Blocker 或 ## 总结 章节")

    # 3. 适配器反向引用
    for adapter in ("CLAUDE.md", "GEMINI.md"):
        p = cwd / adapter
        if p.exists():
            text = p.read_text()
            if "AGENTS.md" not in text:
                warnings.append(f"{adapter}: 缺 AGENTS.md 反向引用")

    # 输出
    if errors:
        print(f"check: {len(errors)} error(s)", file=sys.stderr)
        for e in errors:
            print(f"  ERROR  {e}", file=sys.stderr)

    if warnings and strict:
        print(f"check: {len(warnings)} warning(s) (--strict)", file=sys.stderr)
        for w in warnings:
            print(f"  WARN  {w}", file=sys.stderr)
        sys.exit(1)

    if warnings:
        print(f"check: {len(warnings)} warning(s)")

    if errors:
        sys.exit(1)

    print(f"check: passed ({len(story_files)} stories, {len(review_files)} reviews)")
```

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_check.py -v`
Expected: 3 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement check with full validation suite (TDD)"
```

---

### Task 25: bin/agentrace render

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_render.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_render.py`:

```python
"""测试 bin/agentrace render。"""
import subprocess
from pathlib import Path

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_render_creates_overview(sample_project: Path):
    """render 应生成 docs/agentrace/OVERVIEW.md。"""
    result = run_agents(sample_project, "render")
    assert result.returncode == 0, result.stderr
    overview = sample_project / "docs/agentrace/OVERVIEW.md"
    assert overview.exists()
    content = overview.read_text()
    assert "S-001" in content
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_render.py -v`
Expected: 1 个 test 失败

**Step 3: 实现 render**

替换 `cmd_render` 函数：

```python
def cmd_render(args):
    cwd = Path.cwd()
    stories_dir = cwd / "docs/agentrace/stories"
    reviews_dir = cwd / "docs/agentrace/reviews"

    if not stories_dir.exists():
        print("error: docs/agentrace/stories/ 不存在", file=sys.stderr)
        sys.exit(1)

    by_status: dict[str, list[dict]] = {}
    for f in sorted(stories_dir.glob("S-*.md")):
        fm, _ = _parse_md(f)
        status = fm.get("status", "unknown")
        by_status.setdefault(status, []).append(fm)

    lines = ["# 项目进度概览", "", f"_generated by bin/agentrace render at {datetime.datetime.now().isoformat()}_", ""]

    status_order = ["in_progress", "in_review", "blocked", "planned", "draft", "done", "rejected"]
    for status in status_order:
        if status not in by_status:
            continue
        lines.append(f"## {status} ({len(by_status[status])})")
        lines.append("")
        for s in by_status[status]:
            lines.append(f"- **{s.get('id', '?')}** {s.get('title', '')} (assignee: {s.get('assignee', '—')})")
        lines.append("")

    target = cwd / "docs/agentrace/OVERVIEW.md"
    target.write_text("\n".join(lines))
    print(f"rendered: {target.relative_to(cwd)}")
```

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_render.py -v`
Expected: 1 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement render (TDD)"
```

---

### Task 26: bin/agentrace init

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_init.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_init.py`:

```python
"""测试 bin/agentrace init。"""
import subprocess
from pathlib import Path

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_init_creates_structure(tmp_path: Path):
    """init 应创建 docs/agentrace/stories 等目录。"""
    result = run_agents(tmp_path, "init")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "docs/agentrace/stories").exists()
    assert (tmp_path / "docs/agentrace/reviews").exists()
    assert (tmp_path / "docs/agentrace/inbox").exists()
    assert (tmp_path / "AGENTS.md").exists()


def test_init_refuses_existing(tmp_path: Path):
    """init 应在已存在 AGENTS.md 的目录拒绝。"""
    (tmp_path / "AGENTS.md").write_text("# existing\n")
    result = run_agents(tmp_path, "init")
    assert result.returncode != 0
    assert "exists" in result.stderr.lower() or "已存在" in result.stderr
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_init.py -v`
Expected: 2 个 test 失败

**Step 3: 实现 init**

替换 `cmd_init` 函数：

```python
INIT_FILES: dict[str, str] = {
    "docs/agentrace/stories/_TEMPLATE.md": """---
id: S-NNN
title: <title>
status: draft
author: __USER__
assignee: ""
created: __TODAY__
updated: __TODAY__
depends_on: []
blocks: []
related_reviews: []
related_commits: []
tags: []
priority: P1
blocked_by: ""
---

## 背景

## 范围

## 验收标准

- [ ] 条件 1

## 技术备注

## 实现日志

- __TODAY__  status: draft
""",
    "docs/agentrace/reviews/_TEMPLATE.md": """---
id: R-NNN
story: S-MMM
reviewer: __USER__
created: __TODAY__
based_on_commits: []
iteration: 1
verdict: needs_discussion
addresses_reviews: []
---

## 总结

## Blocker

## 非 Blocker

## 提问 / 讨论

## 关联
""",
    "AGENTS.md": "# AGENTS\n\n## 当前激活 Story\n\n<!-- bin/agentrace sync -->\n\n## 工作流\n\n1. bin/agentrace new-story --title \"...\n2. bin/agentrace advance S-NNN in_progress\n",
}


def cmd_init(args):
    cwd = Path.cwd()
    if (cwd / "AGENTS.md").exists():
        print("error: AGENTS.md 已存在，拒绝覆盖", file=sys.stderr)
        sys.exit(1)

    import getpass
    user = getpass.getuser()
    today = datetime.date.today().isoformat()

    for relpath, content in INIT_FILES.items():
        target = cwd / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        content = content.replace("__USER__", user).replace("__TODAY__", today)
        target.write_text(content)

    print(f"initialized: agentrace模板在 {cwd}")
    print("  下一步: bin/agentrace new-story --title \"第一个 story\"")
```

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_init.py -v`
Expected: 2 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement init (TDD)"
```

---

### Task 26b: bin/agentrace resume & triage（TDD，现场勘查）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_resume.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_resume.py`:

```python
"""测试 bin/agentrace resume / triage。"""
import subprocess
from pathlib import Path

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_resume_clean_workspace(tmp_path: Path):
    """干净工作区下 resume 应提示当前激活 Story 或环境就绪。"""
    run_agents(tmp_path, "init")
    result = run_agents(tmp_path, "resume")
    assert result.returncode == 0, result.stderr
    assert "现场接力简报" in result.stdout or "就绪" in result.stdout


def test_resume_dirty_workspace(tmp_path: Path):
    """有未提交改动时 resume 应提取修改文件与符号提示。"""
    run_agents(tmp_path, "init")
    # 初始化 git
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

    # 制造 dirty 改动
    test_file = tmp_path / "foo.py"
    test_file.write_text("def calculate_tax(amount):\n    return amount * 0.1\n")

    result = run_agents(tmp_path, "resume")
    assert result.returncode == 0, result.stderr
    assert "foo.py" in result.stdout
    assert "calculate_tax" in result.stdout
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_resume.py -v`
Expected: 测试失败

**Step 3: 实现 resume / triage**

在 `bin/agentrace` 中实现 `cmd_resume`（支持 AST 提取 Python 符号及 git status 差异分析）：

```python
def cmd_resume(args):
    cwd = Path.cwd()
    print("==================== 现场接力简报 (Auto-Triaged) ====================")
    
    # 1. 查找当前激活 Story
    stories_dir = cwd / "docs/agentrace/stories"
    active_story = "无"
    if stories_dir.exists():
        for sf in stories_dir.glob("S-*.md"):
            fm, _ = parse_frontmatter(sf.read_text(encoding="utf-8"))
            if fm.get("status") == "in_progress":
                active_story = f"{fm.get('id')} ({fm.get('title', '')})"
                break
    print(f"【中断任务】: {active_story}")

    # 2. Git 状态探测
    dirty_files = []
    try:
        git_st = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if git_st.stdout.strip():
            for line in git_st.stdout.strip().split("\n"):
                dirty_files.append(line.strip())
    except Exception:
        pass

    if dirty_files:
        print(f"【工作区状态】: 存在未提交修改 (Dirty Working Tree: {len(dirty_files)} 文件)")
        for df in dirty_files[:5]:
            print(f"  - {df}")
    else:
        print("【工作区状态】: 干净 (Clean Working Tree)")

    # 3. CodeGraph / AST 符号感知
    symbols = []
    import ast
    for df in dirty_files:
        fname = df.split()[-1]
        fpath = cwd / fname
        if fpath.suffix == ".py" and fpath.exists():
            try:
                tree = ast.parse(fpath.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        symbols.append(f"function `{node.name}` in {fname}")
                    elif isinstance(node, ast.ClassDef):
                        symbols.append(f"class `{node.name}` in {fname}")
            except Exception:
                pass
    if symbols:
        print("【CodeGraph 语义感知】:")
        for sym in symbols[:5]:
            print(f"  - 触及符号: {sym}")

    # 4. 测试探针
    test_files = [f for f in dirty_files if "test" in f]
    if test_files:
        try:
            t_res = subprocess.run(
                ["pytest", "-q"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            print(f"【测试探针当前结果】: returncode={t_res.returncode}")
            lines = [l for l in t_res.stdout.split("\n") if l.strip()]
            for l in lines[-3:]:
                print(f"  {l}")
        except Exception:
            pass

    print("【接力建议】: 请结合上述断点信息直接继续开发或调试。")
    print("========================================================================")
```

并在 argparse 注册 `resume` 和 `triage`（作为别名）。

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_resume.py -v`
Expected: 2 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement resume and triage command (TDD)"
```

---

### Task 26c: bin/agentrace impact（TDD，代码影响面分析）

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_impact.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_impact.py`:

```python
"""测试 bin/agentrace impact。"""
import subprocess
from pathlib import Path

BIN = Path(__file__).parent.parent / "agentrace"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_impact_finds_symbol_callers(tmp_path: Path):
    """impact 命令应能分析某符号在项目中的被调用点。"""
    src_file = tmp_path / "core.py"
    src_file.write_text("def add(a, b):\n    return a + b\n")

    caller_file = tmp_path / "use.py"
    caller_file.write_text("from core import add\nx = add(1, 2)\n")

    result = run_agents(tmp_path, "impact", "add")
    assert result.returncode == 0, result.stderr
    assert "use.py" in result.stdout
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_impact.py -v`
Expected: 测试失败

**Step 3: 实现 impact**

在 `bin/agentrace` 中实现 `cmd_impact`：

> v0.1 实现：使用 Python `ast` 模块扫描所有 .py 文件的 `ast.FunctionDef` / `ast.ClassDef` 节点，给出定义位置 + 简单的文本调用匹配。
> v0.2 路线：真正的 AST 调用链分析（递归跟踪 `ast.Call` 节点的被调函数，处理 attr / chained / 跨文件引用），可接入外部 CodeGraph 索引（如 LSP、tree-sitter、pyright）。

```python
def cmd_impact(args):
    cwd = Path.cwd()
    target_symbol = args.target
    if not target_symbol:
        print("error: 请提供目标符号名或文件名", file=sys.stderr)
        sys.exit(1)

    print(f"【CodeGraph 影响面分析】: 目标 `{target_symbol}`")
    matches = []
    for py_file in cwd.rglob("*.py"):
        if ".pytest_cache" in str(py_file) or "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            if target_symbol in content:
                rel = py_file.relative_to(cwd)
                matches.append(str(rel))
        except Exception:
            pass

    if matches:
        print(f"  关联/调用文件 ({len(matches)} 处):")
        for m in matches:
            print(f"  - {m}")
    else:
        print("  未发现跨文件引用。")
```

并在 argparse 注册 `impact`。

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_impact.py -v`
Expected: test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement impact command (TDD)"
```

---

### Task 27: bin/agentrace install-snippet

**Files:**
- Create: `/Users/jason/python/AI/agentrace/bin/tests/test_install_snippet.py`
- Modify: `/Users/jason/python/AI/agentrace/bin/agentrace`

**Step 1: 写失败测试**

`bin/tests/test_install_snippet.py`:

```python
"""测试 bin/agentrace install-snippet。"""
import subprocess
from pathlib import Path

import pytest

BIN = Path(__file__).parent.parent / "agentrace"
SNIPPETS = Path(__file__).parent.parent.parent / "adapters/snippets"


def run_agents(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BIN), *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_install_snippet_creates_marker(tmp_path: Path, monkeypatch):
    """install-snippet 应在 ~/.claude/CLAUDE.md 加 BEGIN/END 标记。"""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    fake_claude = fake_home / ".claude"
    fake_claude.mkdir()
    (fake_claude / "CLAUDE.md").write_text("# existing\n")

    monkeypatch.setenv("HOME", str(fake_home))
    # 改 install-snippet 路径判断通过 env var 或 monkeypatch
    result = run_agents(tmp_path, "install-snippet", "--agent", "claude")
    assert result.returncode == 0, result.stderr

    installed = (fake_claude / "CLAUDE.md").read_text()
    assert "BEGIN agentrace-protocol" in installed
    assert "END agentrace-protocol" in installed


def test_install_snippet_idempotent(tmp_path: Path, monkeypatch):
    """第二次运行 install-snippet 不应重复追加。"""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    fake_claude = fake_home / ".claude"
    fake_claude.mkdir()
    (fake_claude / "CLAUDE.md").write_text("# existing\n")

    monkeypatch.setenv("HOME", str(fake_home))
    run_agents(tmp_path, "install-snippet", "--agent", "claude")
    first_content = (fake_claude / "CLAUDE.md").read_text()
    run_agents(tmp_path, "install-snippet", "--agent", "claude")
    second_content = (fake_claude / "CLAUDE.md").read_text()
    assert first_content == second_content
```

**Step 2: 跑测试，验证失败**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_install_snippet.py -v`
Expected: 2 个 test 失败

**Step 3: 实现 install-snippet**

替换 `cmd_install_snippet` 函数：

```python
def cmd_install_snippet(args):
    cwd = Path.cwd()
    home = Path.home()

    agents_for_path = {
        "claude": home / ".claude/CLAUDE.md",
        "antigravity": home / ".gemini/config/GEMINI.md",
    }

    snippets_dir = cwd / "adapters/snippets"
    snippet_file_map = {
        "claude": snippets_dir / "claude.md",
        "antigravity": snippets_dir / "antigravity.md",
    }

    targets = [args.agent] if args.agent else list(agents_for_path.keys())

    for agent in targets:
        if agent not in agents_for_path:
            print(f"warning: 未知 agent {agent}，跳过", file=sys.stderr)
            continue

        snippet_path = snippet_file_map[agent]
        target_path = agents_for_path[agent]

        if not snippet_path.exists():
            print(f"warning: {snippet_path} 不存在，跳过 {agent}", file=sys.stderr)
            continue

        snippet_content = snippet_path.read_text()
        target_path.parent.mkdir(parents=True, exist_ok=True)

        existing = target_path.read_text() if target_path.exists() else ""

        # 幂等：检测 BEGIN/END 标记
        import re
        pattern = re.compile(
            r"<!-- BEGIN agentrace-protocol v[\d.]+.*?-->.*?<!-- END agentrace-protocol v[\d.]+.*?-->",
            re.DOTALL,
        )

        if pattern.search(existing):
            new_content = pattern.sub(snippet_content.strip(), existing, count=1)
            action = "updated"
        else:
            new_content = existing.rstrip() + "\n\n" + snippet_content
            action = "appended"

        target_path.write_text(new_content)
        print(f"install-snippet: {action} {target_path}")
```

并替换 argparse：

```python
p_install = subparsers.add_parser("install-snippet")
p_install.add_argument("--agent", default=None)
```

**Step 4: 跑测试**

Run: `cd /Users/jason/python/AI/agentrace && PYTHONPATH=bin python -m pytest bin/tests/test_install_snippet.py -v`
Expected: 2 个 test 通过

**Step 5: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add bin/
git commit -m "feat(bin/agentrace): implement install-snippet with idempotent marker (TDD)"
```

---

## Phase 6: 适配器扩展层

### Task 28: adapters/README.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/adapters/README.md`

**Step 1: 创建文件**

````markdown
# 加一个新 Agent 适配器

例如要加 Cursor / Codex / Aider：

1. **仓库根加适配器文件 `<NAME>.md`**：结构照抄 `CLAUDE.md` / `GEMINI.md`
   - 第 1 行反向引用 `AGENTS.md`
   - 工作流 / Reviewer 边界 / 风格 三段不可少
   - "风味"段改成新 Agent 的工具栈语言

2. **写用户级片段 `adapters/snippets/<name>.md`**
   - 标记必须含版本号，便于未来升级替换
   - 触发条件写清楚（"进入项目前先 ls <触发文件>"）

3. **改 `bin/agentrace install-snippet` 加一段 case**：新 Agent 的用户级配置文件路径

4. **改仓库根 README 加一行**："支持 <新 Agent>"，链接到对应适配器文件

5. **改 `bin/agentrace check`**：增加对新适配器文件的"反向引用 AGENTS.md"校验

## 模板

最小适配器模板：

```markdown
# <NAME>.md — <Agent> 适配器

<!-- 主约定在 ./AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1。

## 工作流（接入 30 秒）

1. Read `AGENTS.md`
2. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. `bin/agentrace check` 一次确保环境干净
4. 干活，commit message 含 `(S-NNN)`

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`
- 不改 `src/`、不改 `status:` 字段

## <Agent> 风味

<!-- 描述此 Agent 的特有工具 / 命令 -->

## 风格

中文回复，无 emoji。
```

## 已支持的适配器

| Agent | 适配器文件 | 用户级片段 |
|-------|-----------|----------|
| Claude Code | `CLAUDE.md` | `adapters/snippets/claude.md` |
| Antigravity | `GEMINI.md` | `adapters/snippets/antigravity.md` |
| Cursor（示例） | `adapters/examples/cursor.md` | — |
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add adapters/README.md
git commit -m "docs: add adapters/README.md (how to add new agent adapter)"
```

---

### Task 29: 用户级片段 claude.md / antigravity.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/adapters/snippets/claude.md`
- Create: `/Users/jason/python/AI/agentrace/adapters/snippets/antigravity.md`

**Step 1: 创建 `claude.md`**

````markdown
<!-- BEGIN agentrace-protocol v0.1 — DO NOT EDIT BETWEEN MARKERS -->
## 多 Agent 协作协议（适用所有 agentrace 派生项目）

**触发条件**：每次进入新工作目录前，先 `ls AGENTS.md`。

如果项目根目录存在 `AGENTS.md`：
1. **热接力探测**：先运行 `bin/agentrace resume`，若存在中断的脏工作区或测试断点，直接获取现场简报继续工作
2. **必读**：若无中断现场，先 `Read` `AGENTS.md`，再 `Read` `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. **状态推进**：完成 Story 后必须 `bin/agentrace advance <id> <new_status>`，不要手改 `status:` 字段
4. **commit 规范**：`<type>: <description> (S-NNN)`，Story ID 必填
5. **拓扑感知**：改动核心模块前可运行 `bin/agentrace impact [symbol]` 查阅影响面
6. **Reviewer 边界**：只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`，不改 `src/`，不直接改 `status:`
7. **跨 Agent 协作**：接手前 `Read` `docs/agentrace/inbox/`，可能有上一个 Agent 留的问题
8. **下一步**：commit 后 `Read` `AGENTS.md` 中"当前激活 Story"表格，更新你的状态

如果项目根目录**没有** `AGENTS.md`：按默认 Claude Code 流程工作，但 commit message 仍推荐带任务 ID（如有）。
<!-- END agentrace-protocol v0.1 -->
````

**Step 2: 创建 `antigravity.md`**

````markdown
<!-- BEGIN agentrace-protocol v0.1 — DO NOT EDIT BETWEEN MARKERS -->
## 多 Agent 协作协议

**触发条件**：每次进入新工作目录前，检查根目录是否有 `AGENTS.md`。

如果存在 `AGENTS.md`：
1. 先运行 `bin/agentrace resume` 探测是否存在突发中断现场
2. 先读取 `AGENTS.md`，再读取 `docs/agentrace/stories/` 中状态为 `in_progress` 的 Story
3. 推进 Story 状态：`bin/agentrace advance <id> <new_status>`，不要直接修改 `status:` 字段
4. commit message 包含 Story ID：`<type>: <desc> (S-NNN)`
5. 关键修改或 Review 建议前可用 `bin/agentrace impact` 分析符号影响面
6. Reviewer 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/` 三个目录
7. 接手前读 `docs/agentrace/inbox/` 看是否有上一个 Agent 留下的便条

如果项目根目录**没有** `AGENTS.md`：按默认 Antigravity 流程工作。
<!-- END agentrace-protocol v0.1 -->
````

**Step 3: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add adapters/snippets/
git commit -m "docs: add user-level protocol snippets for Claude and Antigravity"
```

---

### Task 30: adapters/examples/cursor.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/adapters/examples/cursor.md`

**Step 1: 创建文件**

````markdown
# cursor.md — Cursor 适配器（示例）

<!-- 这是 adapters/examples/ 下的示例，演示如何加新适配器。
     Cursor 用户级配置通常在 ~/.cursor/rules/ 或类似位置。
     本文件仅供参考，不被自动识别。 -->

<!-- 主约定在 ../../AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1。

## 工作流（接入 30 秒）

1. 跑 `bin/agentrace resume` 检查是否有中断现场
2. Read `AGENTS.md`
3. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
4. `bin/agentrace check` 一次确保环境干净
5. 干活，commit message 含 `(S-NNN)`

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`
- 不改 `src/`、不改 `status:` 字段

## Cursor 风味

- 使用 Cursor 的 Cmd+K 内联编辑时，仍遵守上述 Reviewer 边界
- 使用 Cursor Chat（Cmd+L）时，让它先 Read AGENTS.md

## 风格

中文回复，无 emoji。
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add adapters/examples/cursor.md
git commit -m "docs: add Cursor adapter as adapter example"
```

---

## Phase 7: Skill 暴露

### Task 31: .claude/skills/agentrace/SKILL.md

**Files:**
- Create: `/Users/jason/python/AI/agentrace/.claude/skills/agentrace/SKILL.md`

**Step 1: 创建 Skill 文件**

````markdown
---
name: agents
description: |
  agentrace工作流。Resume → Pick Story → Read → Advance → Work → Impact → Commit → Advance → Review。
  当用户提到 "story / S-NNN / advance / review / new-story / resume / triage / impact" 或在 agentrace 派生项目目录下工作时调用。
---

# agentrace Skill

## 触发

- 用户说"接手项目" / "开始新 story" / "推进 S-NNN" / "review 这个 PR" / "把 R-NNN 写一下" / "查影响面"
- 用户 cd 进 agentrace 派生项目（根目录有 AGENTS.md + docs/agentrace/）

## 工作流

1. 运行 `bin/agentrace resume` 探测是否存在未提交改动或测试断点
2. Read `AGENTS.md`（≤ 80 行）
3. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
4. `bin/agentrace check` 一次确保环境干净
5. 按用户意图执行命令：
   - "接力断点" → `bin/agentrace resume`
   - "查影响面" → `bin/agentrace impact <symbol>`
   - "新建 story" → `bin/agentrace new-story --title "..."`
   - "推进 S-NNN 到 X" → `bin/agentrace advance S-NNN X`
   - "review 这个" → `bin/agentrace new-review S-NNN`
   - "校验" → `bin/agentrace check --strict`
6. 操作后跑 `bin/agentrace check` 确认无 error

## Reviewer 边界

只动 `docs/agentrace/reviews/`、`inbox/`、`decisions/`。
其他目录的修改都需先有对应 Story + advance。

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。
````

**Step 2: 提交**

```bash
cd /Users/jason/python/AI/agentrace
git add .claude/skills/agentrace/SKILL.md
git commit -m "feat: expose agentrace workflow as Claude Code Skill"
```

---

## Phase 8: 自检

### Task 32: 在 examples/calculator 上跑 bin/agentrace check --strict 全通过

**Files:**
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/stories/S-001-basic-arithmetic.md`
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/stories/S-002-power-and-errors.md`
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/reviews/R-001-on-S-001.md`
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/reviews/R-002-on-S-002.md`
- Modify: `/Users/jason/python/AI/agentrace/examples/calculator/docs/agentrace/reviews/R-003-on-S-002.md`

**Step 1: 把 `<filled-by-bin-agents-sync>` 占位符替换为真实 commit SHAs**

先在 calculator 目录建立 git 历史（如果还没有）：

```bash
cd /Users/jason/python/AI/agentrace/examples/calculator
git init
git add .
git commit -m "feat: scaffold calculator project"
git commit --allow-empty -m "feat: implement add/sub/mul/div (S-001)"
git commit --allow-empty -m "feat: implement pow with error class split (S-002)"
git commit --allow-empty -m "fix(calculator): add pow(a, 0) case + split errors (S-002)"
git log --oneline
```

Expected: 4 个 commit，记录每个 SHA。

把 S-001 / S-002 / R-001 / R-002 / R-003 中的 `<filled-by-bin-agents-sync>` 替换为对应的真实 SHA（每个文件 1 个，逗号分隔）。

**Step 2: 跑 calculator 自检**

```bash
cd /Users/jason/python/AI/agentrace/examples/calculator
/Users/jason/python/AI/agentrace/bin/agentrace check --strict
```

Expected: `check: passed (4 stories, 3 reviews)`，退出码 0

**Step 3: 如果有 error，修复到通过**

参考 bin/agentrace check 报错逐条修。常见修复：
- 补 frontmatter 必填字段
- 修引用闭合（S-002.related_reviews 中 R-003 必须存在）
- 修 enum 值

**Step 4: 跑示例 pytest**

```bash
cd /Users/jason/python/AI/agentrace/examples/calculator
pytest -v
```

Expected: 全部 8 个 test 通过

**Step 5: 提交 calculator git + 顶层 git**

```bash
# calculator 自身先提交（如果在 calculator 子目录有 git）
cd /Users/jason/python/AI/agentrace/examples/calculator
git add .
git commit -m "docs: fill commit SHAs in stories/reviews" || true

# 顶层仓库
cd /Users/jason/python/AI/agentrace
git add examples/calculator/docs/agentrace/
git commit -m "chore: calculator self-check passes bin/agentrace check --strict"
```

---

## Self-Review Checklist

完成所有 32 个 task 后，逐项核对：

- [ ] Phase 0-1 全部 commit 成功
- [ ] Phase 2 模板文件完整
- [ ] Phase 3 calculator 业务代码 + 测试全通过
- [ ] Phase 4 calculator docs/agentrace/ 完整（4 Story + 3 Review + 1 Decision + ROADMAP）
- [ ] Phase 5 bin/agentrace CLI 8 个命令全部有测试覆盖
- [ ] Phase 6 adapters/ 完整（README + 2 snippets + 1 example）
- [ ] Phase 7 SKILL.md 暴露
- [ ] Phase 8 calculator self-check 全部通过

跑最终的全局 check：

```bash
cd /Users/jason/python/AI/agentrace
PYTHONPATH=bin python -m pytest bin/tests/ -v
# 期望：全部测试通过

bin/agentrace check --strict --project examples/calculator
# 期望：passed
```

---

## 估算

- Task 0-5（仓库脚手架 + 协议根 + handbook）：~6 个 commit，30 分钟
- Task 6-9（模板文件）：~4 个 commit，15 分钟
- Task 10-13（calculator 业务）：~4 个 commit，45 分钟（含测试）
- Task 14-18（calculator docs/agentrace/）：~5 个 commit，30 分钟
- Task 19-27（bin/agentrace CLI）：~9 个 commit，2-3 小时（TDD 含金量最高）
- Task 28-31（适配器 + Skill）：~4 个 commit，20 分钟
- Task 32（自检）：~15 分钟

总计 ~5 小时单人执行；按 subagent-driven 模式并发可能缩短到 2-3 小时。

---

---