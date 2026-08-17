# Review 协议

## Reviewer 边界

Reviewer Agent **只能写**到：

- `docs/agentrace/reviews/`
- `docs/agentrace/inbox/`
- `docs/agentrace/decisions/`（触发架构决策时）

**不能**：

- 改 `src/` 等代码目录
- 改 `stories/<id>.md` 的 `status:` 字段
- 改任何 commit

边界由 `bin/agentrace check` 校验：commit author ≠ Story.assignee 且触及 `status:` 字段时告警"疑似 Reviewer 越权"。

## Verdict 类型

| verdict | 含义 | Story 状态机反应 |
|---------|------|------------------|
| `approved` | 通过，可推进 done | author 调 `advance <id> done` |
| `changes_requested` | 必须返工 | 自动 `advance <id> in_progress` |
| `needs_discussion` | 阻塞，需决策 | Story → blocked，Reviewer 创建 D-NNN |

## 多轮 Review

第 N 轮 review 文件名 `R-NNN-on-S-MMM.md`，frontmatter：

```yaml
---
id: R-NNN
story: S-MMM
iteration: N
addresses_reviews: [R-prev-id]
based_on_commits: [new-commits-only]
verdict: ...
---
```

历史 review 不删除，作为审计记录。

## 何时创建 Decision

Review 中遇到架构 / 接口 / 库选择类问题：

1. 自动创建 `docs/agentrace/decisions/D-NNN-<slug>.md`
2. 在 review body 的"关联"段引用 D-NNN
3. 决策落地后（Decision 状态变 `accepted`），Reviewer 把 review verdict 改为 `approved`

## Review body 必填章节

```
## 总结
## Blocker（必须修复）
## 非 Blocker（建议改进，不阻塞）
## 提问 / 讨论
## 关联
```

`## Blocker` 可为空（表示无 Blocker），但章节必须存在。