"""
Pydantic schemas for calculator API (request/response validation).
"""
from pydantic import BaseModel, Field


class CalculatorOperands(BaseModel):
    """Two operands for a binary operation."""

    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")


class CalculatorResult(BaseModel):
    """Structured result of a calculator operation."""

    operation: str
    a: float
    b: float
    result: float
