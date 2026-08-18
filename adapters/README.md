# Agent 适配层指南 (Adapters)

> **agentrace 是一个中立的、文件驱动（File-based）的多 Agent 协作协议。**
> 
> 协议核心（`AGENTS.md`、`docs/agentrace/` 规范与 `bin/agentrace` 状态机）独立于任何特定模型与工具。目前项目中以 **Claude Code** 与 **Antigravity** 为首批官方先行适配范例（Reference Implementations），用于演示多模型接力、断点现场还原与交叉 Review。
>
> 任何能够读写文件和运行轻量命令的 AI 编码助手（如 **Codex**、**Kimi Code**、**Cursor**、**Windsurf**、**Aider**、**Devin** 等）均可轻松接入。我们非常欢迎社区开发者为喜爱的工具补充适配！

---

## 适配层设计架构：双层机制 (Two-Layer Architecture)

为了避免在每个项目中为不同 Agent 重复编写繁琐规则，agentrace 采用“**用户级全局片段 + 项目级极薄跳板**”的双层架构：

```
全局/用户级环境：
  ~/.claude/CLAUDE.md 或 ~/.gemini/config/GEMINI.md 或 ~/.cursor/rules
  └── 注入 snippet 规则："检测到项目有 AGENTS.md 时，自动激活 agentrace 协议"

项目级工作区：
  项目根目录/
  ├── AGENTS.md              ← 项目宪法 (Single Source of Truth，项目规范与 Story 主表)
  ├── CLAUDE.md / GEMINI.md  ← 极薄适配跳板 (≤ 25 行，首行反向引用 AGENTS.md)
  └── docs/agentrace/        ← 状态机与协作产物 (stories / reviews / decisions / inbox)
```

---

## 适配状态与矩阵

| Agent / 编码助手 | 适配器文件 | 用户级片段 | 状态 | 说明 |
|-----------------|-----------|-----------|------|------|
| **Claude Code** | `CLAUDE.md` | `adapters/snippets/claude.md` | 官方先行范例 | 完整支持 Skill + Snippet 全局安装 |
| **Antigravity (Gemini)** | `GEMINI.md` | `adapters/snippets/antigravity.md` | 官方先行范例 | 完整支持 Rules + Snippet 全局安装 |
| **Kimi Code** | `adapters/examples/kimi.md` | 待共建 | 示例模板 | 欢迎提交全局 Snippet 与 CLI 路径支持 |
| **Codex / OpenAI** | `adapters/examples/codex.md` | 待共建 | 示例模板 | 欢迎提交全局 Instructions 配置 |
| **Cursor** | `adapters/examples/cursor.md` | 待共建 | 示例模板 | 欢迎补充 `.cursorrules` 集成方案 |
| **Windsurf / Cascade** | 待共建 | 待共建 | 欢迎贡献 | 欢迎提交 PR |
| **Aider** | 待共建 | 待共建 | 欢迎贡献 | 欢迎提交 PR |
| **其他 Agent** | 参见下方指南 | 参见下方指南 | 开放扩展 | 仅需 5 分钟即可完成接入 |

---

## 如何添加一个新 Agent 适配器（5 步指引）

为新 Agent 添加适配非常轻量，欢迎通过 Pull Request 贡献到本项目：

### 1. 编写项目级适配器模板

在 `adapters/examples/<name>.md`（或项目根目录 `<NAME>.md`）编写极薄适配文件：
- **第 1 行必须包含反向引用**：`<!-- 主约定在 ./AGENTS.md，先读它。 -->`
- **核心章节**：工作流（接入 30 秒）、Reviewer 边界（只写 reviews/inbox/decisions，不直接改业务代码与 status 字段）、特有风味（该 Agent 的特有工具/快捷键）与风格。

```markdown
# <NAME>.md — <Agent> 适配器

<!-- 主约定在 ./AGENTS.md，先读它。 -->

本项目遵循 agentrace v0.1 多 Agent 协作协议。

## 工作流（接入 30 秒）

1. 跑 `bin/agentrace resume`（如有中断现场）或直接 Read `AGENTS.md`
2. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. Read `docs/agentrace/handbook/story-lifecycle.md` 了解状态机
4. `bin/agentrace check` 一次确保环境干净
5. 干活，commit message 含 `(S-NNN)`

## Reviewer 边界

- 只写 `docs/agentrace/reviews/`、`docs/agentrace/inbox/`、`docs/agentrace/decisions/`
- 不改 `src/` 等业务代码
- 不直接手改 `stories/<id>.md` 的 `status:` 字段（必须 `bin/agentrace advance`）

## <Agent> 风味

<!-- 描述此 Agent 的特有工具 / 命令行 / 快捷键 -->

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。
```

### 2. 编写用户级片段

在 `adapters/snippets/<name>.md` 中编写用于注入到该 Agent 全局配置中的规则片段：
- 必须使用标记包裹版本号（如 `<!-- BEGIN agentrace-protocol v0.1 -->` 与 `<!-- END agentrace-protocol v0.1 -->`），确保未来升级可幂等替换。
- 触发条件明确为：“进入工作目录时，若检测到 `AGENTS.md` 则遵循 agentrace 协议”。

### 3. 注册到 CLI `install-snippet`

在 `bin/agentrace` 的 `cmd_install_snippet` 函数中增加新 Agent 的目标路径映射：

```python
agents_for_path = {
    "claude": home / ".claude/CLAUDE.md",
    "antigravity": home / ".gemini/config/GEMINI.md",
    "kimi": home / ".kimi/config.md",  # 例如
    # ...
}
```

### 4. 完善根目录 README

在 `README.md` 与 `README_zh.md` 的支持矩阵中登记新 Agent。

### 5. 校验与测试

运行 `bin/agentrace check --strict` 和 `pytest` 确保一切通过。