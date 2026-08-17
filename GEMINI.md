# GEMINI.md — Antigravity 适配器

<!-- 主约定在 ./AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1。

## 工作流（接入 30 秒）

1. 跑 `bin/agentrace resume`（如有中断现场）或直接 Read `AGENTS.md`
2. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. Read `docs/agentrace/handbook/story-lifecycle.md` 了解状态机
4. `bin/agentrace check` 一次确保环境干净
5. 干活，commit message 含 `(S-NNN)`

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`
- 不改 `src/` 等代码
- 不改 `stories/<id>.md` 的 `status:` 字段（必须 `bin/agentrace advance`）

## Antigravity 风味

<!-- 待 Antigravity 工具栈确认后补充具体命令 -->

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。