# services/category_service.py
from typing import List

from sqlalchemy.orm import Session

from models import Category


def create_category(session: Session, user_id: int, name: str) -> Category:
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty.")

    existing = (
        session.query(Category)
        .filter(Category.user_id == user_id, Category.name.ilike(name))
        .first()
    )
    if existing:
        raise ValueError(f"Category '{name}' already exists.")

    category = Category(user_id=user_id, name=name)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def list_categories(session: Session, user_id: int) -> List[Category]:
    return (
        session.query(Category)
        .filter(Category.user_id == user_id)
        .order_by(Category.name.asc())
        .all()
    )
