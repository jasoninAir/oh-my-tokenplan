# CLAUDE.md — Claude Code 适配器

<!-- 主约定在 ./AGENTS.md，先读它。 -->

本项目遵循 multiagent 协议 v0.1。

## 工作流（接入 30 秒）

1. 跑 `bin/agents resume`（如有中断现场）或直接 Read `AGENTS.md`
2. Read `docs/agents/stories/` 中 `status: in_progress` 的 Story
3. Read `docs/agents/handbook/story-lifecycle.md` 了解状态机
4. `bin/agents check` 一次确保环境干净
5. 干活，commit message 含 `(S-NNN)`

## Reviewer 边界

- 只写 `docs/agents/reviews/`、`inbox/`、`decisions/`
- 不改 `src/` 等代码
- 不改 `stories/<id>.md` 的 `status:` 字段（必须 `bin/agents advance`）

## Claude Code 风味

- 优先用 `Skill` 工具调预置工作流（`.claude/skills/agents/SKILL.md`）
- 派子任务用 `Agent` 工具
- 改文件前先 `Grep` 定位，避免盲改

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。