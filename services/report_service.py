# services/report_service.py
from calendar import monthrange
from datetime import date
from typing import List, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Expense, Budget, Category


def _month_date_range(year: int, month: int) -> tuple[date, date]:
    last_day = monthrange(year, month)[1]
    start = date(year, month, 1)
    end = date(year, month, last_day)
    return start, end


def get_monthly_total(
    session: Session,
    user_id: int,
    year: int,
    month: int,
) -> float:
    start, end = _month_date_range(year, month)

    total = (
        session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start,
            Expense.date <= end,
        )
        .scalar()
    )
    return float(total or 0.0)


def get_category_summary(
    session: Session,
    user_id: int,
    year: int,
    month: int,
) -> List[Dict]:
    """
    Returns list of dicts:
    {
        "category": str,
        "budget": float | None,
        "spent": float,
        "status": str   # "Under", "Exactly", "Exceeded"
    }
    """
    start, end = _month_date_range(year, month)

    # Get spending per category
    spent_rows = (
        session.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(func.sum(Expense.amount), 0.0).label("spent"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start,
            Expense.date <= end,
        )
        .group_by(Category.id, Category.name)
        .order_by(Category.name.asc())
        .all()
    )

    # Fetch budgets for this month
    budgets = (
        session.query(Budget)
        .join(Category, Category.id == Budget.category_id)
        .filter(
            Budget.user_id == user_id,
            Budget.year == year,
            Budget.month == month,
        )
        .all()
    )

    budgets_by_cat = {b.category_id: b.amount for b in budgets}

    summary: List[Dict] = []
    for row in spent_rows:
        spent = float(row.spent or 0.0)
        budget_amount = budgets_by_cat.get(row.category_id)

        if budget_amount is None:
            status = "No budget"
        else:
            if spent < budget_amount:
                status = "Under"
            elif spent == budget_amount:
                status = "Exactly"
            else:
                status = "Exceeded"

        summary.append(
            {
                "category": row.category_name,
                "budget": budget_amount,
                "spent": spent,
                "status": status,
            }
        )

    return summary


def get_spent_for_category(
    session: Session,
    user_id: int,
    category_id: int,
    year: int,
    month: int,
) -> float:
    start, end = _month_date_range(year, month)

    total = (
        session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(
            Expense.user_id == user_id,
            Expense.category_id == category_id,
            Expense.date >= start,
            Expense.date <= end,
        )
        .scalar()
    )
    return float(total or 0.0)
