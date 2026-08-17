"""核心计算逻辑。"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    value: float
    op: str


class CalculatorError(ValueError):
    """所有领域错误的基类。"""


class ZeroDivisionError_(CalculatorError):
    """除零错误。"""


class NegativeExponentError(CalculatorError):
    """负指数不支持。"""


def add(a: float, b: float) -> Result:
    return Result(float(a + b), "add")


def sub(a: float, b: float) -> Result:
    return Result(float(a - b), "sub")


def mul(a: float, b: float) -> Result:
    return Result(float(a * b), "mul")


def div(a: float, b: float) -> Result:
    if b == 0:
        raise ZeroDivisionError_("division by zero")
    return Result(float(a / b), "div")


def pow(a: float, b: int) -> Result:
    if b < 0:
        raise NegativeExponentError("negative exponent not supported")
    return Result(float(a ** b), "pow")