<!-- BEGIN multiagent-protocol v0.1 — DO NOT EDIT BETWEEN MARKERS -->
## 多 Agent 协作协议（适用所有 multiagent 派生项目）

**触发条件**：每次进入新工作目录前，先 `ls AGENTS.md`。

如果项目根目录存在 `AGENTS.md`：
1. **热接力探测**：先运行 `bin/agents resume`，若存在中断的脏工作区或测试断点，直接获取现场简报继续工作
2. **必读**：若无中断现场，先 `Read` `AGENTS.md`，再 `Read` `docs/agents/stories/` 中 `status: in_progress` 的 Story
3. **状态推进**：完成 Story 后必须 `bin/agents advance <id> <new_status>`，不要手改 `status:` 字段
4. **commit 规范**：`<type>: <description> (S-NNN)`，Story ID 必填
5. **拓扑感知**：改动核心模块前可运行 `bin/agents impact [symbol]` 查阅影响面
6. **Reviewer 边界**：只写 `docs/agents/reviews/`、`inbox/`、`decisions/`，不改 `src/`，不直接改 `status:`
7. **跨 Agent 协作**：接手前 `Read` `docs/agents/inbox/`，可能有上一个 Agent 留的问题
8. **下一步**：commit 后 `Read` `AGENTS.md` 中"当前激活 Story"表格，更新你的状态

如果项目根目录**没有** `AGENTS.md`：按默认 Claude Code 流程工作，但 commit message 仍推荐带任务 ID（如有）。
<!-- END multiagent-protocol v0.1 -->