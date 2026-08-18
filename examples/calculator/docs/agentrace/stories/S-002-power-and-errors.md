---
id: S-002
title: 实现 power + 细化错误处理
status: done
author: claude-impl-A
assignee: claude-impl-A
created: 2026-08-13
updated: 2026-08-16
depends_on:
- S-001
blocks: []
related_reviews:
- R-002
- R-003
related_commits:
- dee42f8
- '1880027'
impacted_symbols:
- pow
- ZeroDivisionError_
- NegativeExponentError
tags:
- core
- errors
priority: P1
blocked_by: ''
---

## 背景

S-001 完成了基础四则运算。本 Story 补全 power 运算，并把单一 `CalculatorError` 拆分为具体子类，便于上层精确捕获。

## 范围

- 实现 `pow(a, b: int)` 函数
- 拆 `CalculatorError` 为 `ZeroDivisionError_` / `NegativeExponentError`
- 不含缓存 / 链式调用（走 S-004）

## 验收标准

- [x] `pow(2, 10).value == 1024`
- [x] `pow(5, 0).value == 1`
- [x] `pow(2, -1)` 抛 `NegativeExponentError`
- [x] `div(1, 0)` 抛 `ZeroDivisionError_`（不再是 `CalculatorError`）
- [x] pytest 全部通过，覆盖率 ≥ 90%
- [x] R-002 提到的 Blocker 全部修复

## 技术备注

- power 只支持非负整数指数，负指数抛错（不引入分数运算复杂度）
- 错误类用 `CalculatorError` 基类 + 子类模式，方便 `except CalculatorError` 兜底
- 名字加下划线避免与 builtin `ZeroDivisionError` 冲突

## 实现日志

- 2026-08-13  status: draft → planned
- 2026-08-13  status: planned → in_progress
- 2026-08-13  commit: implement pow + split error classes
- 2026-08-14  status: in_progress → in_review
- 2026-08-14  changes_requested by R-002
                  - 缺 pow(a, 0) 边界 case
                  - 错误类型用 CalculatorError 太粗
- 2026-08-15  status: in_review → in_progress (返工)
- 2026-08-15  commit: add pow(a, 0) case + split ZeroDivisionError_/NegativeExponentError
- 2026-08-15  status: in_progress → in_review
                  @antigravity 请 re-review
- 2026-08-16  approved by R-003
- 2026-08-16  status: in_review → done