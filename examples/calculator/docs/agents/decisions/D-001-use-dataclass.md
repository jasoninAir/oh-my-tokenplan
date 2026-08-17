---
id: D-001
title: 使用 dataclass 表达 Result 而非 dict
status: accepted
created: 2026-08-10
---

## 状态

accepted (2026-08-10)

## 上下文

S-001 需要为四则运算返回结果。候选：

1. `dict`：轻，但无类型提示
2. `dataclass`：类型安全 + frozen 保证不可变
3. `tuple`：最快但语义弱
4. `pydantic.BaseModel`：重，引入外部依赖

## 决策

采用 **dataclass(frozen=True)**（方案 2）。

理由：

- 不可变（frozen）保证函数式风格
- IDE / mypy / pyright 全部支持
- 零额外依赖
- 与 S-002 错误处理（也用 dataclass 化的 Error 层级）风格一致

## 影响

- Result 类型 `{ value: float, op: str }`
- 错误类继承 `CalculatorError`，具体子类 `ZeroDivisionError_` / `NegativeExponentError`
- 测试用 `isinstance(r, Result)` 验证