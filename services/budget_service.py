# services/budget_service.py
from sqlalchemy.orm import Session

from models import Budget


def set_budget(
    session: Session,
    user_id: int,
    category_id: int,
    year: int,
    month: int,
    amount: float,
) -> Budget:
    if amount <= 0:
        raise ValueError("Budget amount must be positive.")

    budget = (
        session.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.year == year,
            Budget.month == month,
        )
        .first()
    )

    if budget:
        budget.amount = amount
    else:
        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            year=year,
            month=month,
            amount=amount,
        )
        session.add(budget)

    session.commit()
    session.refresh(budget)
    return budget


def get_budget_for_category(
    session: Session,
    user_id: int,
    category_id: int,
    year: int,
    month: int,
) -> Budget | None:
    return (
        session.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.year == year,
            Budget.month == month,
        )
        .first()
    )
