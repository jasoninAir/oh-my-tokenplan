# agentrace v0.1 设计文档

**日期**: 2026-08-17  
**状态**: 设计完成（已引入 Post-Mortem 现场勘查与 CodeGraph 拓扑感知增强）  

---

## 1. 目标与背景

### 1.1 背景痛点
开发者通常订阅了多个 Token Plan（例如 Claude Pro/Team 5 小时限额、Antigravity/Gemini、OpenAI 等）。当一个主力 Agent 在高强度编码中突然遭遇 5 小时 Quota 耗尽（429 熔断）时，需要由另一个 Agent 立即接替继续推进，不能丢失开发上下文与心智模型。

由于 **Agent 无法自知额度何时突然耗尽**，系统不能假设 Agent A 在下线前有自知之明去主动保存快照，而必须依靠**“事后被动现场勘查（Post-Mortem Triage）”**与**代码图谱（CodeGraph / AST）**在接力瞬间完成断点还原。

### 1.2 核心目标
设计一套**通用、可复用**的多 Agent 协作模板（meta 工具），让任意项目 clone 后填具体内容即可：

- 任意 Agent（Claude Code / Antigravity / Cursor / 未来其他）接入项目目录后，**通过文本（markdown 文件）与轻量 CLI 即可无缝接力开发**
- **突发中断零损接力**：前任 Agent 意外下线后，接盘 Agent 通过 `bin/agentrace resume` 一秒还原未提交修改、涉及符号、下游影响及当前测试报错
- **代码拓扑语义感知**：借助 CodeGraph / AST 提取影响面（Callers / Callees / Blast Radius），避免接力 Agent 消耗宝贵 Token 盲目全仓探索
- 多 Agent 之间可以**交替开发、接力开发、相互 Review**
- 项目开发与具体 Agent **解耦**：所有上下文、进度、Review 全部 file-based，Review 过程把建议写到文档便于追溯

---

## 2. 核心决策汇总

| 维度 | 决策 | 动机与说明 |
|------|------|------------|
| 目标产物 | 通用模板 + 示例演示项目（calculator） | 即拷即用，示例覆盖完整生命周期 |
| Agent 适配 | 核心 Claude Code / Antigravity + 适配器层 | 支持不同 Agent 接入，统一使用项目规范 |
| 协作颗粒度 | Feature / Story 级别（含状态机） | 状态机强约束：draft → planned → in_progress → in_review → done |
| 突发中断接力 | **事后现场勘查（Post-Mortem Triage）** | 不依赖 Agent A 自知，Agent B 运行 `bin/agentrace resume` 提取 Git 脏工作区 + 符号拓扑 + 测试探针 |
| 拓扑感知工具 | **CodeGraph / AST 影响面分析** | 通过 `bin/agentrace impact` 分析改动符号的上下游调用链，杜绝 Token 浪费在全仓盲搜 |
| Review 边界 | Reviewer 只提建议、不动代码 | 严格隔离实现者与审查者权限，防止代码冲突与越权 |
| 目录布局 | 扁平 `AGENTS.md` + `docs/agentrace/` | 单点真相（Single Source of Truth），业务与元数据分离 |
| 自动化程度 | 薄脚本层（CLI + check）+ 文件约定 | Python 3.10+ 标准库 + PyYAML，轻量可靠 |
| 整体方案 | 方案 A（文档优先 + 脚本可选用） + 拓扑与探针辅助 | 纯文本为本，脚本提供状态机强校验与极速现场还原 |

---

## 3. 顶层目录结构

```
agentrace/                              # 模板仓库根
├── AGENTS.md                            # 项目主入口（single source of truth）
├── README.md                            # 人类上手文档
├── LICENSE
├──
├── CLAUDE.md                            # → Claude Code 适配器（极薄，≤ 25 行）
├── GEMINI.md                            # → Antigravity 适配器（极薄，≤ 25 行）
├── adapters/                            # 其他 Agent 适配器入口
│   ├── README.md                        #   "如何加新适配器"
│   ├── snippets/                        #   用户级配置片段
│   │   ├── claude.md                    #   追加到 ~/.claude/CLAUDE.md
│   │   └── antigravity.md               #   追加到 Antigravity 全局规则
│   └── examples/                        #   适配器示例（如 cursor.md）
│
├── docs/
│   └── agents/                          # 协作主干
│       ├── plan/ROADMAP.md
│       ├── stories/                     # 一个 Story 一个 .md
│       │   ├── _TEMPLATE.md
│       │   ├── S-001-xxx.md
│       │   └── S-002-xxx.md
│       ├── reviews/                     # 一个 Review 一个 .md
│       │   ├── _TEMPLATE.md
│       │   └── R-001-on-S-001.md
│       ├── decisions/                   # 架构决策 (ADR 风格)
│       │   └── D-001-use-yaml-frontmatter.md
│       ├── inbox/                       # 临时便条
│       │   └── README.md
│       └── handbook/                    # 协议详细文档
│           ├── story-lifecycle.md
│           ├── review-protocol.md
│           ├── relay-and-triage.md      # 接力与现场还原手册
│           └── conventions.md
├──
├── bin/                                 # 薄脚本层
│   └── agents                           # CLI（Python 3.10+，仅标准库 + PyYAML）
│                                        # 命令: init / new-story / advance / check / sync / render / resume / triage / impact
├──
├── examples/calculator/                 # 示例项目（演示完整状态机与接力路径）
│   ├── pyproject.toml
│   ├── src/calculator/core.py
│   ├── tests/test_core.py
│   ├── docs/agentrace/
│   │   ├── stories/S-001..S-004.md
│   │   ├── reviews/R-001..R-003.md
│   │   ├── decisions/D-001.md
│   │   └── plan/ROADMAP.md
│   └── README.md
│
└── .gitignore
```

---

## 4. 两层提示词结构

```
┌──────────────────────────────────────────────────────────────┐
│  用户级（User-Level）— ~/.claude/CLAUDE.md / Antigravity 规则 │
│  内容：通用协议纪律（不依赖具体项目）                            │
│  ─────────────────────────────────────────────────────────── │
│  • 接手项目先检查是否需要热接力：运行 bin/agentrace resume        │
│  • 若无中断现场，再 Read AGENTS.md 与当前激活 Story           │
│  • 完成 Story 推进状态：bin/agentrace advance <id> <status>      │
│  • Reviewer 只动 reviews/ / inbox/ / decisions/               │
│  • commit message 必须含 Story ID: feat: xxx (S-001)          │
│  • 接手前可查看 docs/agentrace/inbox/ 便条                       │
└──────────────────────────────────────────────────────────────┘
                               ↓ 叠加
┌──────────────────────────────────────────────────────────────┐
│  项目级（Project-Level）— <project>/AGENTS.md                  │
│  内容：本项目业务上下文 + 当前激活 Story 索引                  │
│  ─────────────────────────────────────────────────────────── │
│  • 项目简介 / 架构速览                                        │
│  • 当前激活 Story 表（bin/agentrace sync 维护）                  │
│  • 路线图 / 工作流 / 约定 / 已知坑                             │
└──────────────────────────────────────────────────────────────┘
```

**用户级片段用 markdown 注释标记**（`<!-- BEGIN agentrace-protocol v0.1 -->` / `<!-- END -->`），`bin/agentrace install-snippet` 幂等替换。

---

## 5. 突发熔断接力与 CodeGraph 拓扑感知机制

### 5.1 现场勘查机制（Post-Mortem Triage）
当 Agent A 因 429 熔断突然断开时，Agent B 接手只需运行：
```bash
bin/agentrace resume
# 或 bin/agentrace triage
```

CLI 将自动完成四步合成输出：
1. **Git 差异捕捉**：扫描未 commit 的 dirty 文件与 staged diff。
2. **CodeGraph / AST 拓扑关联**：分析受影响的函数/类符号及其上下游调用链（Callers / Callees）。
3. **静默测试探针**：自动运行受影响模块的单测，提取当前红灯（Failure/Error）的具体堆栈与断言。
4. **生成 20 行极简接力简报**：
   ```text
   ==================== 现场接力简报 (Auto-Triaged) ====================
   【中断任务】: S-001 (实现基础除法与异常保护)
   【工作区状态】: 存在未提交修改 (Dirty Working Tree)
     - 修改文件: src/calculator/core.py (L40-L55)
   【CodeGraph 语义感知】:
     - 触及符号: function `divide(a, b)`
     - 依赖影响: 2 个调用方 (tests/test_core.py, src/api/handler.py)
   【测试探针当前结果】: 
     - ❌ FAIL: tests/test_core.py::test_divide_by_zero (抛出 ZeroDivisionError，未封装)
     - ✅ PASS: 其余 11 个测试通过
   【接力建议】:
     - 修复 core.py 中的除零捕获逻辑，使 test_divide_by_zero 转绿，提交 commit (S-001)。
   ========================================================================
   ```

### 5.2 符号影响面分析（`bin/agentrace impact`）
Agent 在修改关键模块或 Review 前，可运行：
```bash
bin/agentrace impact [file_or_symbol]
```
CLI 基于 AST / CodeGraph 扫描项目，输出受该符号修改波及的所有模块与测试用例，辅助生成精准的 Review 或补全测试。

---

## 6. Story 状态机与文件格式

### 6.1 状态机
```
                 ┌──────────┐
                 │  draft   │
                 └────┬─────┘
        author 确认 ──┤
                      ▼
                 ┌──────────┐
       ┌────────│ planned  │
       │        └────┬─────┘
       │ assignee 接手 │
       │             ▼
       │        ┌──────────┐
       │        │in_progress│
       │        └────┬─────┘
       │ 提交 review  │
       │             ▼
       │        ┌──────────┐
       │        │in_review │
       │        └────┬─────┘
       │             │
   ┌───┴────┐        │ review verdict
   │blocked │        │
   └────────┘        │
                ┌────┴────┐
                ▼         ▼
           ┌────────┐ ┌────────┐
           │  done  │ │rejected│→ 回到 in_progress
           └────────┘ └────────┘
```

### 6.2 转换规则

| from → to | 触发者 | 附加条件 |
|-----------|--------|----------|
| draft → planned | author | `## 验收标准` ≥ 1 条 |
| planned → in_progress | 任何人 | `assignee:` 已填 |
| in_progress → in_review | assignee | `related_commits` ≥ 1 |
| in_review → done | 任何人 | 关联 review `verdict: approved` |
| in_review → in_progress | 自动 | 关联 review `verdict: changes_requested` |
| any → blocked | 任何人 | `blocked_by:` 非空 |
| blocked → 原状态 | 解除者 | 删 `blocked_by:` |

**唯一改 `status:` 的方式**：`bin/agentrace advance <id> <new>`。

### 6.3 Story frontmatter
```yaml
---
id: S-001                              # 必填，与文件名一致
title: 实现折扣规则引擎                 # 必填
status: in_progress                    # 必填，状态机枚举
author: claude-impl-A                  # 必填
assignee: claude-impl-A                # 可空
created: 2026-08-17                    # 必填
updated: 2026-08-17                    # 必填，bin/agentrace 自动维护
depends_on: []                         # 依赖 Story IDs
blocks: []                             # 阻塞 Story IDs（自动维护）
related_reviews: [R-001]               # 关联 Review IDs
related_commits: [abc1234]             # commit SHAs（自动从 git log 提取）
impacted_symbols: []                   # CodeGraph 提取的影响符号（可选/自动更新）
tags: [pricing, core]
priority: P1                           # P0/P1/P2/P3
blocked_by: ""                         # blocked 时填写
---
```

---

## 7. Review 协议与文件格式

### 7.1 Reviewer 边界
Reviewer Agent **只能写**：
- `docs/agentrace/reviews/`
- `docs/agentrace/inbox/`
- `docs/agentrace/decisions/`（触发架构决策时）

**不能**：改 src/ 等代码目录、改 `stories/<id>.md` 的 `status:`、改 commit。

### 7.2 Review frontmatter
```yaml
---
id: R-001
story: S-001                           # 必填
reviewer: antigravity-review-A         # 推荐填
created: 2026-08-17
based_on_commits: [abc1234, def5678]   # 必填
iteration: 1                           # 第几轮
verdict: approved                      # approved / changes_requested / needs_discussion
addresses_reviews: []                  # follow-up 时填上轮 ID
---
```

---

## 8. `bin/agentrace` CLI 全集

```bash
init [--example] [--user-snippet]   # 项目初始化
install-snippet [--agent <name>]    # 幂等安装用户级片段
resume                              # 【核心接力】现场勘查：提取脏工作区、符号影响与测试探针
triage                              # resume 的别名
impact [target]                     # 【代码图谱】分析指定文件或改动符号的上下游调用拓扑
new-story [--title] [--tags]       # 创建 Story
new-review <story-id>               # 创建 Review
advance <story-id> <new-status>     # 状态推进（唯一改 status 的方式）
sync                                # 同步 AGENTS.md 表格 + Git commits 关联
check [--strict] [--fix]            # 校验全集
render                              # 生成 OVERVIEW.md
```

---

## 9. `check` 校验规则（22 条）

| # | 类别 | 规则 | 严重度 |
|---|------|------|--------|
| 1 | frontmatter | 必填字段存在 | error |
| 2 | frontmatter | 枚举值合法 | error |
| 3 | frontmatter | 日期 ISO 8601 | error |
| 4 | 引用闭合 | Story.depends_on 引用的 S-NNN 存在 | error |
| 5 | 引用闭合 | Story.related_reviews 引用的 R-NNN 存在 | error |
| 6 | 引用闭合 | Review.story 引用的 S-NNN 存在 | error |
| 7 | 引用闭合 | Review.addresses_reviews 引用的 R-NNN 存在 | error |
| 8 | 唯一性 | S/R/D ID 全局唯一 | error |
| 9 | 唯一性 | 文件名 slug 与 title 一致性 hint | warning |
| 10 | 状态机 | status 与 changelog 最后一次转换一致 | error |
| 11 | 状态机 | advance (from, to) 合法 | error |
| 12 | commit | Story.related_commits SHA 在 git 存在 | error |
| 13 | commit | commit message 含 `(S-NNN)` | warning |
| 14 | Review | 同一 (R-NNN, S-MMM) 不允许多次 | error |
| 15 | Review | body 必有 "## Blocker" 或 "## 总结" | warning |
| 16 | Reviewer 边界 | commit 改 status: 且 author ≠ assignee | warning |
| 17 | Reviewer 边界 | commit 改 src/ 但无关联 Story | warning |
| 18 | AGENTS.md | 必填章节存在 | error |
| 19 | 适配器 | CLAUDE.md / GEMINI.md 含 "Read AGENTS.md" | error |
| 20 | Inbox | inbox/*.md 超 30 天未处理 | warning |
| 21 | changelog | 每个 status 转换对应一行 | warning |
| 22 | 接力一致性 | `status: in_progress` 时若有 dirty 工作区给出接力提示 | info |

---

## 10. 完整文档清单

- 仓库根 `README.md`（5 分钟上手 + 对比表）
- `docs/agentrace/handbook/story-lifecycle.md`（状态机详细）
- `docs/agentrace/handbook/review-protocol.md`（Review 详细）
- `docs/agentrace/handbook/relay-and-triage.md`（热接力与现场还原手册）
- `docs/agentrace/handbook/conventions.md`（命名 / 格式 / commit）
- `docs/agentrace/plan/ROADMAP.md`（路线图模板）
- `docs/agentrace/inbox/README.md`（inbox 用法）
- `docs/agentrace/decisions/D-001-use-yaml-frontmatter.md`（ADR 示例）
- `adapters/README.md`（如何加新适配器）

---

## 11. 非目标 / 边界

- **不做**：自动派发任务给云端 Agent（由人类在 Agent 间切换）；自动合并冲突 commit
- **不做**：Web UI / 复杂服务端云同步
- **不做**：重型外部依赖（CLI 严格维持 Python 3.10+ 标准库 AST + PyYAML，无重型数据库）