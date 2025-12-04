# app.py
from datetime import datetime

from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models import User, Category
from services.category_service import create_category, list_categories
from services.budget_service import set_budget, get_budget_for_category
from services.expense_service import add_expense
from services.report_service import (
    get_monthly_total,
    get_category_summary,
    get_spent_for_category,
)


def get_or_create_default_user(session: Session) -> User:
    """
    For simplicity, we use a single default user.
    """
    user = session.query(User).first()
    if user:
        return user

    user = User(name="Default User", email="default@example.com")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def choose_category(session: Session, user_id: int) -> Category | None:
    categories = list_categories(session, user_id)
    if not categories:
        print("No categories yet. Please create one first.")
        return None

    print("\nAvailable categories:")
    for idx, cat in enumerate(categories, start=1):
        print(f"{idx}. {cat.name}")

    choice = input("Select category number: ").strip()
    if not choice.isdigit():
        print("Invalid choice.")
        return None

    idx = int(choice)
    if 1 <= idx <= len(categories):
        return categories[idx - 1]

    print("Invalid choice.")
    return None


def handle_add_category(session: Session, user: User) -> None:
    name = input("Enter new category name: ").strip()
    try:
        category = create_category(session, user.id, name)
        print(f"Category '{category.name}' created.")
    except ValueError as e:
        print(f"Error: {e}")


def handle_set_budget(session: Session, user: User) -> None:
    category = choose_category(session, user.id)
    if not category:
        return

    year_str = input("Enter year (e.g. 2025): ").strip()
    month_str = input("Enter month (1-12): ").strip()
    amount_str = input("Enter budget amount: ").strip()

    try:
        year = int(year_str)
        month = int(month_str)
        amount = float(amount_str)

        budget = set_budget(session, user.id, category.id, year, month, amount)
        print(
            f"Budget set for category '{category.name}' "
            f"({month}/{year}) = {budget.amount:.2f}"
        )
    except ValueError as e:
        print(f"Error: {e}")


def handle_add_expense(session: Session, user: User) -> None:
    category = choose_category(session, user.id)
    if not category:
        return

    amount_str = input("Enter expense amount: ").strip()
    date_str = input("Enter date (YYYY-MM-DD, blank = today): ").strip()
    desc = input("Enter description (optional): ").strip()

    try:
        amount = float(amount_str)
    except ValueError:
        print("Amount must be a number.")
        return

    if date_str:
        try:
            expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format.")
            return
    else:
        expense_date = datetime.today().date()

    try:
        expense = add_expense(
            session,
            user_id=user.id,
            category_id=category.id,
            amount=amount,
            expense_date=expense_date,
            description=desc,
        )
        print(f"Expense of {expense.amount:.2f} added in '{category.name}'.")

        # --- Budget checks (alerts) ---
        year = expense_date.year
        month = expense_date.month

        budget = get_budget_for_category(session, user.id, category.id, year, month)
        if budget:
            spent = get_spent_for_category(session, user.id, category.id, year, month)
            remaining = budget.amount - spent

            if remaining < 0:
                print(
                    f"⚠ ALERT: You exceeded the budget for '{category.name}' "
                    f"in {month}/{year}. "
                    f"Budget: {budget.amount:.2f}, Spent: {spent:.2f}"
                )
            else:
                ten_percent = 0.1 * budget.amount
                if remaining <= ten_percent:
                    print(
                        f"⚠ WARNING: Only {remaining:.2f} left in your "
                        f"'{category.name}' budget for {month}/{year}."
                    )
    except ValueError as e:
        print(f"Error: {e}")


def handle_monthly_summary(session: Session, user: User) -> None:
    year_str = input("Enter year (e.g. 2025): ").strip()
    month_str = input("Enter month (1-12): ").strip()

    try:
        year = int(year_str)
        month = int(month_str)
    except ValueError:
        print("Year and month must be numbers.")
        return

    total = get_monthly_total(session, user.id, year, month)
    print(f"\nTotal spending in {month}/{year}: {total:.2f}")


def handle_category_report(session: Session, user: User) -> None:
    year_str = input("Enter year (e.g. 2025): ").strip()
    month_str = input("Enter month (1-12): ").strip()

    try:
        year = int(year_str)
        month = int(month_str)
    except ValueError:
        print("Year and month must be numbers.")
        return

    rows = get_category_summary(session, user.id, year, month)
    if not rows:
        print("No expenses recorded for that month.")
        return

    print(f"\nSpending vs Budget for {month}/{year}:")
    print("-" * 60)
    print(f"{'Category':<20}{'Budget':>10}{'Spent':>10}{'Status':>15}")
    print("-" * 60)
    for row in rows:
        budget_str = (
            f"{row['budget']:.2f}" if row["budget"] is not None else "None"
        )
        spent_str = f"{row['spent']:.2f}"
        print(
            f"{row['category']:<20}{budget_str:>10}{spent_str:>10}{row['status']:>15}"
        )
    print("-" * 60)


def print_menu() -> None:
    print("\n=== Expense Tracker CLI ===")
    print("1. Add category")
    print("2. Set / update budget")
    print("3. Add expense")
    print("4. View total spending for a month")
    print("5. View spending vs budget per category")
    print("6. Exit")


def main():
    init_db()
    session = SessionLocal()

    try:
        user = get_or_create_default_user(session)

        while True:
            print_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                handle_add_category(session, user)
            elif choice == "2":
                handle_set_budget(session, user)
            elif choice == "3":
                handle_add_expense(session, user)
            elif choice == "4":
                handle_monthly_summary(session, user)
            elif choice == "5":
                handle_category_report(session, user)
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid option, please try again.")

    finally:
        session.close()


if __name__ == "__main__":
    main()
