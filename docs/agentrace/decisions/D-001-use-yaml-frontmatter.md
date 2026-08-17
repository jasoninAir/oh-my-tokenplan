---
id: D-001
title: 使用 YAML frontmatter 而非 JSON 或 TOML
status: accepted
created: 2026-08-10
---

## 状态

accepted (2026-08-10)

## 上下文

markdown 文件需要存元数据（id、status、created 等）。
候选方案：

1. YAML frontmatter（GitHub 渲染友好，解析库多）
2. JSON frontmatter（严格但丑）
3. TOML frontmatter（Python 友好但工具支持弱）
4. 完全无 frontmatter，元数据靠文件名推断（脆弱）

## 决策

采用 **YAML frontmatter**（方案 1）。

理由：

- GitHub / VSCode / Antigravity 全部原生渲染
- Python `pyyaml` 已是事实标准
- 注释语法 `#` 方便 inline 注解
- 与现有 ADR 工具（adr-tools）生态兼容

## 影响

- 所有 .md 文件必有 frontmatter
- `bin/agentrace check` 校验必填字段
- 文件名 slug 仅作可读性，元数据以 frontmatter 为准