---
id: S-004
title: Calculator 加缓存，记住上次运算
status: blocked
author: claude-impl-A
assignee: ''
created: 2026-08-14
updated: 2026-08-15
depends_on:
- S-001
blocks: []
related_reviews: []
related_commits: []
impacted_symbols: []
tags:
- perf
- caching
priority: P3
blocked_by: 需 D-002 决策：缓存失效策略（LRU vs TTL vs 永不过期）
---

## 背景

calculator 库每次调用 `add(1, 2)` 都重算。如果能记住上次结果，省去重复计算。

## 范围

- 在 `Calculator` 类加 `last_result` 字段
- 提供 `cache_clear()` 方法
- 不含线程安全（季度外）

## 验收标准

- [ ] `Calculator().add(1, 2).last_result == Result(3, "add")`
- [ ] `Calculator().cache_clear()` 后 `last_result is None`
- [ ] 缓存策略符合 D-002 决策

## 技术备注

缓存策略依赖架构决策 D-002。

## 实现日志

- 2026-08-14  status: draft → planned
- 2026-08-15  status: planned → blocked
                  @antigravity 请给 D-002 决策（缓存策略）
                  blocked_by: 缓存失效策略未定