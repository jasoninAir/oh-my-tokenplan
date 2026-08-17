# Inbox

跨 Agent 的临时便条。**不阻塞** Story，但被 `bin/agentrace check` 跟踪。

## 何时写

- 上一个 Agent 跑完发现的下个 Agent 可能踩的坑
- Reviewer 提问但作者暂时没回
- "这件事以后要做"的备忘
- 跨项目的想法

## 何时处理

每周或在 Story 推进时扫一次：

- 可执行 → 转成 Story（`bin/agentrace new-story`，inbox 条目链接过去）
- 不可执行 → 留在这里，加 `#hold` 或 `#wontfix` 标签
- 已解决 → 删除或归档到 `inbox/archive/`

## 文件命名

- `I-NNN-<slug>.md`（有 ID）
- 或 `<YYYY-MM-DD>-<slug>.md`（无 ID，便条性质）

## frontmatter

```yaml
---
id: I-003                    # 可选
created: 2026-08-17
from: claude-impl-A          # 谁留的
tags: [follow-up, perf]
status: open                 # open / hold / wontfix / done
---
```

## 模板

```
## 问题

<描述>

## 建议下一步

- 转成 Story：bin/agentrace new-story
- 或加 #hold / #wontfix
```