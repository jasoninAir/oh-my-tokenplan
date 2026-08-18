# agentrace (oh-my-tokenplan)

> **每一个 Agent 的操作，都留下清晰的轨迹。**
>
> 专为 AI 编码助手设计的多 Agent 协作与接力协议。当主力 Agent 遭遇配额熔断（如 Claude 5 小时限额）时，下一个 Agent 能在 20 秒内无损接力——上下文零丢失，绝无重复造轮子。

[English](README.md) | [简体中文](README_zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests: 39 passing](https://img.shields.io/badge/tests-39%20passing-brightgreen.svg)](bin/tests/)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange.svg)](.claude/skills/agentrace/SKILL.md)

---

## 核心痛点

你在日常编码中使用 Claude Code，工作了一小时突然触发 5 小时配额墙，不得不切换到 Antigravity（Gemini）、Cursor、Codex 或 Kimi Code。此时你不得不从头开始向新 Agent 解释项目背景与当前进度。新 Agent 重新阅读整个代码库，反复提问，甚至理解偏差，让你瞬间回到原点。

或者：Agent A 编写了一项功能，你想让 Agent B 进行审查（Code Review），但两个工具之间缺乏清晰的审查交接协议。

或者：面对长期维护的大型项目，不同的日子使用不同的 Agent 与会话，没有任何人记得昨天的上下文与决策细节。

**agentrace 的解决方案：将多 Agent 协同与接力问题，转化为中立、统一规范的文件系统（File-based）问题。**

## 核心功能

| 典型场景 | agentrace 解决方案 |
|---------|-------------------|
| Agent A 编写中途触发配额熔断 | `bin/agentrace resume` → 20 行精炼交接简报，新 Agent 秒级还原现场 |
| Agent B 审查 Agent A 的代码 | `bin/agentrace new-review S-001` → 审查者只输出 Markdown 评审意见，严格不改动源码 |
| 跨日期、跨工具、多会话持续开发 | 所有工作进度沉淀于 `docs/agentrace/`（Markdown）；任意 Agent 均可接续推进 |
| “修改这个函数会导致哪些下游崩溃？” | `bin/agentrace impact divide` → 基于 AST 的代码爆炸半径（Blast-Radius）拓扑分析 |
| 任务变更历史丢失 | 每次状态流转自动追加至对应 Story 的变更日志（Changelog）中 |
| 协作状态机与元数据混乱 | `bin/agentrace check --strict` 强校验 YAML 元数据、状态跃迁合法性与文件引用完整性 |
| 接入已有项目 | `bin/agentrace onboard` → 自动扫描项目结构并生成初始化落地规划 |

## 30 秒极速演示

> *提示：以下演示以「Claude Code 编写 + Antigravity 审查」作为典型场景，实际可灵活组合 Codex、Kimi Code、Cursor、Windsurf、Aider 等任意 Agent。*

```bash
# 全局安装一次（注册 Claude Code Skill 与用户级配置片段）
git clone https://github.com/jasoninAir/oh-my-tokenplan.git agentrace
cd agentrace
bin/agentrace install

# 在任意项目中初始化
cd ~/your-project
agentrace init

# 对 Claude Code 说：
#   "创建一个实现用户登录的 Story"
#
# Claude Code 将执行：
agentrace new-story --title "implement user login"
# → 创建: docs/agentrace/stories/S-001-implement-user-login.md

# 对 Claude Code 说：
#   "我认领 S-001，开始工作"
#
# Claude Code 将执行：
agentrace advance S-001 in_progress

# ... 编写代码，并在 git commit 描述中附加 "(S-001)" ...

agentrace advance S-001 in_review

# 对 Antigravity 说：
#   "审查 S-001"
#
# Antigravity 将执行：
agentrace new-review S-001
# → 创建: docs/agentrace/reviews/R-001-on-S-001.md
# （输出审查裁决与阻断项，完全不触碰 src/ 源码）

# 切换回 Claude Code："根据 R-001 审查结果，将 S-001 推进至 done"
agentrace advance S-001 done
```

## 运作机制

```
                用户级配置片段 (~/.claude/CLAUDE.md / Antigravity 规则 / 各 Agent 配置)
                  ↓ "检测到 AGENTS.md？遵循 agentrace 协议"
                ┌────────────────────────────┐
                │ 项目级主入口 (AGENTS.md)    │
                │   - 项目背景与架构          │
                │   - 当前激活 Story 列表     │
                │   - 开发规范与代码约定      │
                └────────────────────────────┘
                  ↓ Agent 读取以下标准文档
                ┌────────────────────────────┐
                │ docs/agentrace/            │
                │   stories/   S-NNN-*.md    │
                │   reviews/   R-NNN-*.md    │
                │   decisions/ D-NNN-*.md    │
                │   inbox/     I-NNN-*.md    │
                │   handbook/  协议与规范     │
                └────────────────────────────┘
                  ↓ 轻量 CLI 脚本实施校验
                ┌────────────────────────────┐
                │ bin/agentrace              │
                │   advance / check / resume │
                │   new-story / new-review   │
                │   sync / render / impact   │
                │   onboard / install        │
                └────────────────────────────┘
```

每个协作实体都是一份 `.md` 文件。状态机流转由 `bin/agentrace check` 强行约束。审查者（Reviewer）绝不会意外篡改代码，因为审查输出被限定在 `reviews/`、`inbox/`、`decisions/` 目录中。

## 核心概念

| 概念 | 作用 | 示例 |
|------|------|------|
| **Story** (`S-NNN`) | 最小工作单元，拥有严格状态机：`draft → planned → in_progress → in_review → done` | "实现基础算术运算" |
| **Review** (`R-NNN-on-S-MMM`) | 审查 Agent 出具的裁决（Verdict）与阻断项（Blockers） | "approved" / "changes_requested" |
| **Decision** (`D-NNN`) | ADR 风格的架构与技术决策记录 | "使用 dataclass 实现 Result" |
| **Inbox** (`I-NNN`) | 跨 Agent 异步留言与便签，不阻塞 Story 状态 | "TODO: 评估缓存淘汰策略" |
| **Resume / Triage** | 事后现场勘查简报 | 未提交脏文件 + AST 符号列表 + 测试探针结果 |

状态机跃迁图：

```
draft ──→ planned ──→ in_progress ──→ in_review ──→ done
              ↑           ↓                ↓
              └──────── blocked ──────────┘
                  (审查意见为 changes_requested 时回退到 in_progress)
```

## CLI 命令速查

```bash
agentrace init                    # 在当前项目中初始化 agentrace 骨架
agentrace onboard                 # 自动扫描项目结构并生成初始化分步规划
agentrace install                 # 全局安装 Claude Code Skill 与用户级注入片段
agentrace uninstall               # 卸载全局 Skill 与配置片段
agentrace install-snippet         # 幂等安装用户级片段（按 Agent 类型）

agentrace new-story --title "…"   # 创建 S-NNN-<slug>.md 任务文档
agentrace new-review S-001        # 为指定 Story 创建审查文档 R-NNN-on-S-001.md

agentrace advance S-001 in_progress   # 严格依照状态机推进 Story 状态
agentrace sync                    # 刷新 AGENTS.md 当前 Story 表格及影响符号
agentrace check [--strict]        # 校验 YAML 前置元数据、引用完整性与状态机合法性
agentrace render                  # 重新生成聚合文档 docs/agentrace/OVERVIEW.md

agentrace resume                  # 事后现场勘查：提取未提交改动 + AST 符号 + 测试探针
agentrace triage                  # resume 的同义别名
agentrace impact <symbol>         # 基于 AST 分析改动符号的影响面（爆炸半径）
```

## 安装与配置

### 作为 Claude Code Skill 安装（推荐）

```bash
git clone https://github.com/jasoninAir/oh-my-tokenplan.git agentrace
cd agentrace
bin/agentrace install
```

该命令会将 Skill 拷贝至 `~/.claude/skills/agentrace/`，并将调度规则追加至 `~/.claude/CLAUDE.md`。此后只要你进入任何包含 `AGENTS.md` 与 `docs/agentrace/` 的项目，Claude Code 都会自动激活该协议。

### 单项目独立接入

```bash
cd your-project
cp -r /path/to/agentrace/bin ./
cp -r /path/to/agentrace/docs/agentrace ./
cp -r /path/to/agentrace/AGENTS.md /path/to/agentrace/CLAUDE.md /path/to/agentrace/GEMINI.md ./
bin/agentrace init
```

## 完整示例演示

请查看 `examples/calculator/` —— 这是一个仅 60 行代码的 Python 演示项目，展示了完整的协作状态机生命周期：

| Story | 路径 | 演示特性 |
|-------|------|----------|
| S-001 | draft → planned → in_progress → in_review → done | 一次性审查通过（First-pass approval） |
| S-002 | ... → in_review → in_progress → in_review → done | 两轮审查与返工重写（Changes requested） |
| S-003 | draft → planned | 待实现的长期规划，正文中包含 TODO 引导 |
| S-004 | draft → planned → blocked | 因架构方案未决而被阻断的 Story |

```bash
cd examples/calculator
../../bin/agentrace check --strict
# → check: passed (4 stories, 3 reviews)

../../bin/agentrace resume
# → 打印 20 行极简现场交接简报，包含当前 Story、未提交修改、涉及 AST 符号与测试状态
```

## `agentrace check` 实施的强制约束

1. **`status:` 字段神圣不可手改**：必须通过 `bin/agentrace advance` 修改。手动编辑会被 CI/Check 标记为错误。
2. **Commit 必须携带 Story ID**：提交信息需包含 `(S-NNN)` 格式。`agentrace sync` 会自动采集并关联提交哈希。
3. **Reviewer 绝不修改业务代码**：审查者 Agent 仅被允许写入 `reviews/`、`inbox/`、`decisions/`。
4. **审查记录只增不删（Append-only）**：所有历史审查均作为可追溯的审计轨迹保留，禁止直接覆盖或删除。
5. **所有 `.md` 必须具备合规的 YAML Frontmatter**：字段缺失或非法将无法通过 `agentrace check --strict`。

## 适配层生态与多 Agent 支持

> **协议中立性声明**：agentrace 本身是一套中立的、文件驱动（File-based）的多 Agent 协同标准。当前文档与代码中主要以 **Claude Code** 与 **Antigravity** 为先行落地参考实现（Reference Implementations），但协议**完全适用于任何具备文件读写与命令执行能力的 AI 编程工具**。

### 支持矩阵

| Agent / 编程助手 | 适配器文件 | 用户级全局片段 | 适配状态 | 说明 |
|-----------------|-----------|--------------|---------|------|
| **Claude Code** | `CLAUDE.md` | `adapters/snippets/claude.md` | 官方先行范例（稳定） | 支持 Skill + Snippet 一键全局安装 |
| **Antigravity (Gemini)** | `GEMINI.md` | `adapters/snippets/antigravity.md` | 官方先行范例（稳定） | 支持 Rules + Snippet 全局安装 |
| **Kimi Code** | `adapters/examples/kimi.md` | 待共建 | 示例模板（开箱即用） | 欢迎补充用户级配置注入路径 |
| **Codex / OpenAI** | `adapters/examples/codex.md` | 待共建 | 示例模板（开箱即用） | 欢迎补充 Instructions 模板 |
| **Cursor** | `adapters/examples/cursor.md` | 待共建 | 示例模板（开箱即用） | 欢迎补充 `.cursorrules` 规则联动 |
| **Windsurf / Cascade** | 待共建 | 待共建 | 欢迎贡献 | 欢迎提交 PR |
| **Aider / Devin / 其他** | 参见适配指南 | 参见适配指南 | 开放接入 | 仅需 5 分钟即可完成适配 |

### 如何扩展或贡献一个新 Agent 适配器？

agentrace 采用“**用户级全局片段 + 项目级极薄跳板**”的双层架构，为新 Agent 添加适配极其轻量（通常不超过 25 行配置）：

1. **创建项目级适配器**：在 `adapters/examples/<name>.md`（或项目根目录 `<NAME>.md`）编写跳板文件，第一行反向引用 `AGENTS.md`。
2. **编写用户级片段**：在 `adapters/snippets/<name>.md` 编写带有版本标记的全局 Prompt 规则。
3. **注册 CLI 路径**：在 `bin/agentrace` 的 `cmd_install_snippet` 中注册新 Agent 的全局配置路径。
4. **提交 PR 完善生态**：欢迎向本仓库提交 Pull Request，让更多开发者受益！

详细适配步骤与模板规范请见：[Agent 适配层指南 (adapters/README.md)](adapters/README.md)。

## 设计哲学

- **文件系统优于数据库（File-based > Database）**：每一次状态转移都是一个纯文本 Markdown 文件，无隐藏状态，天然 Git 友好。
- **脚本强约束，人类与 LLM 讲逻辑**：`bin/agentrace` 拦截非法流转，LLM 专注于高价值编码与评审。
- **严格隔离审查权限**：实现代码的 Agent 与审查代码的 Agent 角色解耦，拥有明确的读写权限边界。
- **双层 Prompt 架构**：用户级全局配置规范行为纪律，项目级 `AGENTS.md` 提供领域上下文。
- **核心模块零外部依赖**：仅依赖 Python 3.10+ 标准库与 PyYAML。
- **事后勘查优先，不设事前检查点**：Agent 无需预测额度何时耗尽，接盘 Agent 通过现场勘查一秒还原上下文。

## 路线图

- [ ] v0.2: 真正的 AST 调用图深度分析（目前 v0.1 基于文本正则与 `ast.FunctionDef`）
- [ ] v0.3: PyPI 官方包分发（支持 `pip install agentrace`）
- [ ] v0.4: VS Code / Cursor 扩展（自动感知并高亮 `AGENTS.md` 任务状态）
- [ ] v0.5: 扩展官方适配矩阵（丰富 Kimi Code, Codex, Windsurf, Aider 等内置 Snippets）
- [ ] v1.0: 多语言（Node.js / Rust / Go）开箱即用示例项目

## 参与贡献

热烈欢迎提交 Issue 和 Pull Request！我们尤其欢迎以下维度的贡献：
- 🛠️ **新增 Agent 适配器**：为 Codex、Kimi Code、Windsurf、Aider 等工具贡献适配器与安装脚本（见 [adapters/README.md](adapters/README.md)）
- 📐 **示例项目丰富**：提供不同技术栈或架构模式的多 Agent 接力案例
- 🔍 **核心工具链优化**：AST 分析算法优化、状态机校验完善

本协议崇尚极简——凡是引入重度外部依赖或复杂工具链的提议将被谨慎评估。我们衡量的基准是：“这个改动能否在 60 行的演示库（`examples/calculator`）中保持简洁清晰？”

## 开源协议

MIT — 详见 [LICENSE](LICENSE)。

## 灵感来源

- **Git** — 每一个 commit 都是一个不可变对象；agentrace 的 stories 亦是如此。
- **邮件列表归档（Mailing Lists）** — 所有讨论发生于公开、持久的纯文本中。
- **事后现场分析（Post-Mortem）文化** — 当系统异常中断，下一位响应者依靠现场痕迹还原真相，而非前任的未竟意图。

为将 AI 视为真实协作伙伴而非不可控黑盒的开发者打造。
