# services/expense_service.py
from datetime import date

from sqlalchemy.orm import Session

from models import Expense


def add_expense(
    session: Session,
    user_id: int,
    category_id: int,
    amount: float,
    expense_date: date,
    description: str | None = None,
) -> Expense:
    if amount <= 0:
        raise ValueError("Expense amount must be positive.")

    expense = Expense(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        date=expense_date,
        description=description or "",
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense
