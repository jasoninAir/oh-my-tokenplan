---
id: S-001
title: 实现基础四则运算 add/sub/mul/div
status: done
author: claude-impl-A
assignee: claude-impl-A
created: 2026-08-10
updated: 2026-08-12
depends_on: []
blocks: []
related_reviews: [R-001]
related_commits: ["a1b2c3d", "e4f5g6h"]
impacted_symbols: [add, sub, mul, div]
tags: [core]
priority: P1
blocked_by: ""
---

## 背景

calculator 库的第一个 Story。四则运算是任何计算器的基础。

## 范围

- 实现 `add` / `sub` / `mul` / `div`
- div 处理除零错误
- 不含 power（走 S-002）

## 验收标准

- [x] 4 个函数全部实现，返回 `Result` dataclass
- [x] `div(1, 0)` 抛 `CalculatorError`
- [x] pytest 全部通过
- [x] 测试覆盖率 ≥ 90%

## 技术备注

- `Result` 用 `dataclass(frozen=True)`（见 D-001）
- 错误类型先用单一 `CalculatorError`，细化推迟到 S-002
- 输入统一转 `float` 保证类型一致

## 实现日志

- 2026-08-10  status: draft → planned
- 2026-08-11  status: planned → in_progress (assignee=claude-impl-A)
- 2026-08-11  commit: add/sub/mul/div skeleton with NotImplementedError
- 2026-08-11  commit: implement add/sub/mul/div + div-by-zero guard
- 2026-08-12  status: in_progress → in_review
- 2026-08-12  approved by R-001
- 2026-08-12  status: in_review → done