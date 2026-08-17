import pytest
from calculator import (
    CalculatorError,
    NegativeExponentError,
    Result,
    ZeroDivisionError_,
    add,
    div,
    mul,
    pow,
    sub,
)


def test_add_returns_result_dataclass():
    r = add(1, 2)
    assert isinstance(r, Result)
    assert r.value == 3
    assert r.op == "add"


def test_sub():
    assert sub(5, 3).value == 2


def test_mul():
    assert mul(3, 4).value == 12


def test_div():
    assert div(10, 2).value == 5


def test_div_by_zero_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError_):
        div(1, 0)


def test_pow_positive_exponent():
    assert pow(2, 10).value == 1024


def test_pow_zero_exponent():
    assert pow(5, 0).value == 1


def test_pow_negative_exponent_raises():
    with pytest.raises(NegativeExponentError):
        pow(2, -1)