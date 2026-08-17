---
name: agents
description: |
  multiagent 协议工作流。Pick Story → Read → Advance → Work → Commit → Advance → Review。
  当用户提到 "story / S-NNN / advance / review / new-story" 或在 multiagent 派生项目目录下工作时调用。
---

# multiagent 协议 Skill

## 触发

- 用户说"开始新 story" / "推进 S-NNN" / "review 这个 PR" / "把 R-NNN 写一下"
- 用户 cd 进 multiagent 派生项目（根目录有 AGENTS.md + docs/agents/）

## 工作流

1. Read `AGENTS.md`（≤ 80 行）
2. Read `docs/agents/stories/` 中 `status: in_progress` 的 Story
3. `bin/agents check` 一次确保环境干净
4. 按用户意图执行命令：
   - "新建 story" → `bin/agents new-story --title "..."`
   - "推进 S-NNN 到 X" → `bin/agents advance S-NNN X`
   - "review 这个" → `bin/agents new-review S-NNN`
   - "校验" → `bin/agents check --strict`
5. 操作后跑 `bin/agents check` 确认无 error

## Reviewer 边界

只动 `docs/agents/reviews/`、`inbox/`、`decisions/`。
其他目录的修改都需先有对应 Story + advance。

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。