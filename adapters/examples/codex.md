# CODEX.md — Codex / OpenAI Coding Assistant 适配器（示例）

<!-- 这是 adapters/examples/ 下的示例，演示如何为 Codex / OpenAI 编码助手等工具增加适配。
     用户级配置通常位于全局 instructions 或 CLI 配置文件中。
     本文件仅供参考，使用时可复制到项目根目录并命名为 CODEX.md。 -->

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
- 不直接手改 `stories/<id>.md` 的 `status:` 字段（必须通过 `bin/agentrace advance` 状态机指令推进）

## Codex 风味

- 遵循单点职责原则，严守命令与状态机跃迁纪律
- 审查或编码前优先利用 `bin/agentrace resume` 还原上下文现场

## 风格

中文回复，无 emoji，TODO 用 `<!-- TODO: ... -->` 注释。
