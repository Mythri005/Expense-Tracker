# models.py
from datetime import date

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)

    categories = relationship("Category", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    expenses = relationship("Expense", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="categories")

    budgets = relationship("Budget", back_populates="category")
    expenses = relationship("Expense", back_populates="category")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_category_name"),
    )


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="budgets")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="budgets")

    month = Column(Integer, nullable=False)  # 1–12
    year = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "month", "year",
                         name="uq_user_category_month_year"),
    )


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="expenses")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="expenses")

    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    description = Column(String(255))
