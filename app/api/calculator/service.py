"""
Calculator business logic: arithmetic operations with validation.
"""
from fastapi import HTTPException, status

from app.api.calculator.schemas import CalculatorOperands, CalculatorResult


def add(operands: CalculatorOperands) -> CalculatorResult:
    """Return a + b."""
    return CalculatorResult(
        operation="add",
        a=operands.a,
        b=operands.b,
        result=operands.a + operands.b,
    )


def subtract(operands: CalculatorOperands) -> CalculatorResult:
    """Return a - b."""
    return CalculatorResult(
        operation="subtract",
        a=operands.a,
        b=operands.b,
        result=operands.a - operands.b,
    )


def multiply(operands: CalculatorOperands) -> CalculatorResult:
    """Return a * b."""
    return CalculatorResult(
        operation="multiply",
        a=operands.a,
        b=operands.b,
        result=operands.a * operands.b,
    )


def divide(operands: CalculatorOperands) -> CalculatorResult:
    """Return a / b. Raises HTTPException on divide-by-zero."""
    if operands.b == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Division by zero is not allowed",
        )
    return CalculatorResult(
        operation="divide",
        a=operands.a,
        b=operands.b,
        result=operands.a / operands.b,
    )
