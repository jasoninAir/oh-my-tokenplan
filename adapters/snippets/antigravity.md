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