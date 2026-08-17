# AGENTS.md — calculator 示例

> 本文件是 calculator 子项目的 single source of truth。
> CLAUDE.md / GEMINI.md 只是适配器。

## 项目简介

calculator 是 agentrace的 demo 项目：一个 mini Python 库，演示完整状态机路径。

## 当前激活 Story

<!-- bin/agentrace sync -->

| ID | 标题 | 状态 | 负责人 |
|----|------|------|--------|
| S-001 | 实现基础四则运算 add/sub/mul/div | done | claude-impl-A |
| S-002 | 实现 power + 细化错误处理 | done | claude-impl-A |
| S-003 | 写 calculator README 文档 | planned | — |
| S-004 | Calculator 加缓存，记住上次运算 | blocked | — |



## 路线图

本季度目标：calculator v0.1。

## 工作流

1. Read 本文件
2. Read `docs/agentrace/stories/` 中 `status: in_progress` 的 Story
3. 跑 `bin/agentrace check` 一次
4. 干活，commit message 含 `(S-NNN)`

## 约定

- commit: `<type>: <desc> (S-NNN)`
- 中文回复，无 emoji

## 详细文档

- 状态机：`../docs/agentrace/handbook/story-lifecycle.md`
- Review 协议：`../docs/agentrace/handbook/review-protocol.md`