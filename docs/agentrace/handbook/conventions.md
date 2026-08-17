# 命名与格式约定

## ID 体系

- Story: `S-NNN`（3 位补零，全局递增）
- Review: `R-NNN-on-S-MMM`
- Decision: `D-NNN`
- Inbox: `I-NNN`（可选，也可不用 ID）

ID 由 `bin/agentrace new-*` 自动分配，禁止手写。

## 文件名

`<ID>-<slug>.md`，slug 是小写连字符英文：

- `S-001-basic-arithmetic.md`
- `R-001-on-S-001.md`
- `D-001-use-dataclass.md`

slug 不必与 title 完全一致，但要能识别主题。

## commit message

```
<type>: <description> (S-NNN)
```

- type: feat / fix / refactor / docs / test / chore
- 必含一个 Story ID
- 多 Story 关联：`feat: x (S-001, S-003)`

`bin/agentrace sync` 从 git log 提取并更新 `Story.related_commits`。

## 章节约定

Story body 章节顺序固定：

```
## 背景
## 范围
## 验收标准
## 技术备注
## 实现日志（changelog，不要手编辑）
```

Review body：

```
## 总结
## Blocker（必须修复）
## 非 Blocker（建议）
## 提问 / 讨论
## 关联
```

Decision body（ADR 风格）：

```
## 状态（proposed / accepted / deprecated）
## 上下文
## 决策
## 影响
```

## YAML frontmatter 必填字段

| 文件类型 | 必填 |
|---|---|
| Story | id / title / status / author / created / updated |
| Review | id / story / verdict / reviewer / created / based_on_commits |
| Decision | id / title / status / created |

## 日期格式

ISO 8601：`YYYY-MM-DD`