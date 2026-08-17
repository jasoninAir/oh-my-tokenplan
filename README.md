# multiagent

> 多 Agent 协作的 file-based 协议。
> Claude Code、Antigravity 或其他 Agent 接入任何派生项目，靠 markdown + 薄脚本就能交接。

## 一句话

把项目开发和 Agent 解耦：所有上下文、进度、Review 都写在 `docs/agents/` 的 markdown 里，
任意 Agent cd 进项目读完 AGENTS.md 就能上手，不依赖任何代码层 API。

## 5 分钟上手

### 在新项目使用本模板

```bash
mkdir my-project && cd my-project
git init
cp -r /path/to/multiagent/. .
bin/agents install-snippet   # 把通用纪律装到 ~/.claude/CLAUDE.md
```

然后编辑 `AGENTS.md` 填项目简介，`bin/agents new-story --title "..."` 开始第一个 Story。

### 接手一个已有项目（multiagent 派生）

1. 跑 `bin/agents resume`（如有中断现场）或直接 `Read AGENTS.md`
2. 读 `docs/agents/stories/` 中 `status: in_progress` 的 Story
3. 读 `docs/agents/handbook/story-lifecycle.md` 了解状态机
4. 跑 `bin/agents check` 确认环境干净
5. 接手：填 `assignee`，调 `bin/agents advance <id> in_progress`

## 目录约定

| 路径 | 作用 |
|------|------|
| `AGENTS.md` | 项目主入口（single source of truth） |
| `CLAUDE.md` / `GEMINI.md` | Claude Code / Antigravity 适配器（≤ 25 行） |
| `adapters/` | 适配器模板 + 用户级片段 |
| `docs/agents/stories/` | 一个 Story 一个 .md |
| `docs/agents/reviews/` | 一个 Review 一个 .md |
| `docs/agents/decisions/` | 一个 Decision 一个 .md (ADR 风格) |
| `docs/agents/inbox/` | 跨 Agent 临时便条 |
| `docs/agents/handbook/` | 协议详细文档 |
| `bin/agents` | 薄脚本 CLI |
| `examples/calculator/` | 完整状态机路径示例 |

## 设计原则

- **File-based 优先**：状态、进度、Review 全部 markdown，无数据库
- **状态机由脚本强制**：不能手改 status，必须 `bin/agents advance`
- **Reviewer 只提建议**：不直接改 src/
- **两层提示词**：用户级纪律 + 项目级上下文，互不污染
- **适配器极薄**：核心约束都在 AGENTS.md，新增 Agent 工具只需加 25 行
- **突发熔断接力**：通过 `bin/agents resume` 现场勘查，零损切换 Agent

## 详细文档

- 状态机：`docs/agents/handbook/story-lifecycle.md`
- Review 协议：`docs/agents/handbook/review-protocol.md`
- 接力与现场勘查：`docs/agents/handbook/relay-and-triage.md`
- 命名约定：`docs/agents/handbook/conventions.md`
- 适配器开发：`adapters/README.md`

## 状态

v0.1（设计完成，实现进行中）

## License

MIT