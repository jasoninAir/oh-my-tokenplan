# 加一个新 Agent 适配器

例如要加 Cursor / Codex / Aider：

1. **仓库根加适配器文件 `<NAME>.md`**：结构照抄 `CLAUDE.md` / `GEMINI.md`
   - 第 1 行反向引用 `AGENTS.md`
   - 工作流 / Reviewer 边界 / 风格 三段不可少
   - "风味"段改成新 Agent 的工具栈语言

2. **写用户级片段 `adapters/snippets/<name>.md`**
   - 标记必须含版本号，便于未来升级替换
   - 触发条件写清楚（"进入项目前先 ls <触发文件>"）

3. **改 `bin/agentrace install-snippet` 加一段 case**：新 Agent 的用户级配置文件路径

4. **改仓库根 README 加一行**："支持 <新 Agent>"，链接到对应适配器文件

5. **改 `bin/agentrace check`**：增加对新适配器文件的"反向引用 AGENTS.md"校验

## 模板

最小适配器模板：

```markdown
# <NAME>.md — <Agent> 适配器

<!-- 主约定在 ./AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1。

## 工作流（接入 30 秒）

1. Read `AGENTS.md`
2. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. `bin/agentrace check` 一次确保环境干净
4. 干活，commit message 含 `(S-NNN)`

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`inbox/`、`decisions/`
- 不改 `src/`、不改 `status:` 字段

## <Agent> 风味

<!-- 描述此 Agent 的特有工具 / 命令 -->

## 风格

中文回复，无 emoji。
```

## 已支持的适配器

| Agent | 适配器文件 | 用户级片段 |
|-------|-----------|----------|
| Claude Code | `CLAUDE.md` | `adapters/snippets/claude.md` |
| Antigravity | `GEMINI.md` | `adapters/snippets/antigravity.md` |
| Cursor（示例） | `adapters/examples/cursor.md` | — |