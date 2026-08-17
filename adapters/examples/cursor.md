# cursor.md — Cursor 适配器（示例）

<!-- 这是 adapters/examples/ 下的示例，演示如何加新适配器。
     Cursor 用户级配置通常在 ~/.cursor/rules/ 或类似位置。
     本文件仅供参考，不被自动识别。 -->

<!-- 主约定在 ../../AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1。

## 工作流（接入 30 秒）

1. 跑 `bin/agentrace resume`（如有中断现场）或直接 Read `AGENTS.md`
2. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. `bin/agentrace check` 一次确保环境干净
4. 干活，commit message 含 `(S-NNN)`

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`
- 不改 `src/`、不改 `status:` 字段

## Cursor 风味

- 使用 Cursor 的 Cmd+K 内联编辑时，仍遵守上述 Reviewer 边界
- 使用 Cursor Chat（Cmd+L）时，让它先 Read AGENTS.md

## 风格

中文回复，无 emoji。