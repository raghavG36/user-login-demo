"""
Calculator routes: add, subtract, multiply, divide (all JWT-protected).
"""
from fastapi import APIRouter, Depends

from app.api.auth.router import get_current_user
from app.api.calculator.schemas import CalculatorOperands, CalculatorResult
from app.api.calculator.service import add as calc_add, subtract as calc_subtract, multiply as calc_multiply, divide as calc_divide
from app.db.models import User

router = APIRouter(prefix="/calculator", tags=["calculator"])


@router.post("/add", response_model=CalculatorResult)
async def add(
    body: CalculatorOperands,
    current_user: User = Depends(get_current_user),
):
    """Add two numbers. Requires JWT."""
    return calc_add(body)


@router.post("/subtract", response_model=CalculatorResult)
async def subtract(
    body: CalculatorOperands,
    current_user: User = Depends(get_current_user),
):
    """Subtract b from a. Requires JWT."""
    return calc_subtract(body)


@router.post("/multiply", response_model=CalculatorResult)
async def multiply(
    body: CalculatorOperands,
    current_user: User = Depends(get_current_user),
):
    """Multiply two numbers. Requires JWT."""
    return calc_multiply(body)


@router.post("/divide", response_model=CalculatorResult)
async def divide(
    body: CalculatorOperands,
    current_user: User = Depends(get_current_user),
):
    """Divide a by b. Returns 400 on divide-by-zero. Requires JWT."""
    return calc_divide(body)
