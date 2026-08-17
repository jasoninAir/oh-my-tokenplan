# Story 生命周期

## 状态机

```
draft → planned → in_progress → in_review → done
              ↑           ↓              ↓
              └───────────┴── blocked ───┘
                 (changes_requested 也回 in_progress)
```

完整转换表：

| from → to | 触发者 | 附加条件 |
|-----------|--------|----------|
| draft → planned | author | `## 验收标准` 章节 ≥ 1 条 |
| planned → in_progress | 任何人 | `assignee:` 已填 |
| in_progress → in_review | assignee | `related_commits` ≥ 1 |
| in_review → done | 任何人 | 关联 review `verdict: approved` |
| in_review → in_progress | 自动 | 关联 review `verdict: changes_requested` |
| any → blocked | 任何人 | `blocked_by:` 非空 |
| blocked → 原状态 | 解除者 | 删 `blocked_by:` |

唯一改 `status:` 的方式：`bin/agents advance <id> <new>`。
手改会被 `bin/agents check` 报错。

## 阻塞与解锁

blocked 状态必须有：
- `blocked_by:` 字段，说明卡在哪
- 实现日志追加一行 `@<角色> 请帮助`（@antigravity / @claude-impl-A / @human）

解锁方式：
- 关联的 D-NNN 决策落地后，删 `blocked_by:` 并 `advance` 回原状态
- 或 `assignee` 主动说明已自行解决

## changelog 维护

每个状态转换**必须**对应一行 changelog：

```
- 2026-08-17 10:00  status: in_progress → in_review
                  commits: [abc1234]
                  @antigravity 请 review
```

`bin/agents advance` 自动追加，手写无效。

## 工作流示例

**Agent A 接 S-001**：

```bash
# 1. 接手
bin/agents advance S-001 in_progress   # status: planned → in_progress

# 2. 写代码
git commit -m "feat: implement basic arithmetic (S-001)"

# 3. 提交 review
bin/agents advance S-001 in_review    # status: in_progress → in_review
                                       # 自动写 changelog，列 commits
```

**Agent B 接手 review**：

```bash
# 1. 写 review
# 创建 docs/agents/reviews/R-001-on-S-001.md，verdict: approved

# 2. Agent A 据此 advance 到 done
bin/agents advance S-001 done         # 自动校验有关联 approved review
```