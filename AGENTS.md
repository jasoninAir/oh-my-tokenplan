# AGENTS.md — agentrace模板

> 本文件是 agentrace 模板的 single source of truth。
> CLAUDE.md / GEMINI.md 等各 Agent 适配器均为薄跳板，所有约束与规范都源自本文件。
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
- [x] AGENTS.md / CLAUDE.md / GEMINI.md
- [x] handbook 三件（story-lifecycle / review-protocol / conventions / relay-and-triage）
- [ ] bin/agentrace CLI 实现
- [ ] examples/calculator 完整数据
- [ ] 适配器片段 + install-snippet 幂等机制
- [ ] 自检：bin/agentrace check --strict 全通过

## 工作流（给新 Agent 的最短路径）

1. Read 本文件
2. Read `docs/agentrace/handbook/story-lifecycle.md`（状态机详细）
3. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
4. 跑 `bin/agentrace resume`（如有中断现场）或 `bin/agentrace check`（干净接手）
5. 干活：commit message 含 `(S-NNN)`
6. 调 `bin/agentrace advance <id> in_review` 提交 review
7. Reviewer Agent 写 `docs/agentrace/reviews/R-NNN-on-S-MMM.md`

## 约定

- commit message: `<type>: <description> (S-NNN)`
- 中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释
- Review 写在 `docs/agentrace/reviews/`，不直接改代码
- 不手改 `status:`，必须 `bin/agentrace advance`
- 新 ID 由 `bin/agentrace new-*` 自动分配，禁止手写
- 改动核心模块前可跑 `bin/agentrace impact <symbol>` 查影响面

## 已知坑

- `bin/agentrace install-snippet` 的 Antigravity 路径待官方文档验证
- PyYAML 已是 conda ai 环境默认依赖，但其他环境需 `pip install pyyaml`

## 详细文档

- 状态机：`docs/agentrace/handbook/story-lifecycle.md`
- Review 协议：`docs/agentrace/handbook/review-protocol.md`
- 接力与现场勘查：`docs/agentrace/handbook/relay-and-triage.md`
- 命名 / 格式 / commit：`docs/agentrace/handbook/conventions.md`
- 决策记录：`docs/agentrace/decisions/`
- Inbox：`docs/agentrace/inbox/`
- 路线图：`docs/agentrace/plan/ROADMAP.md`
- 适配器开发：`adapters/README.md`
- 设计文档：`docs/superpowers/specs/2026-08-17-agentrace-protocol-design.md`