**Expense Tracker – Python CLI Application**

This project is built for the L7 Informatics Internship Assignment.
It is a simple terminal-based Python application to track expenses, set budgets, and view monthly summaries.
SQLite is used as the database and SQLAlchemy as the ORM.

**Features**

1. Add categories

2. Set monthly budgets

3. Log daily expenses

4. Alerts when budget is exceeded

5. Warning when only ~10% budget is left

6. View total spending per month

7. View spending vs budget per category

**How to Run (Local)**
1. Create & activate virtual environment
  python -m venv venv
  venv\Scripts\activate     (Windows)

3. Install dependencies
  pip install -r requirements.txt

4. Run the application
  python app.py

**Docker Instructions**

**Build image**

docker build -t expense-tracker-cli .

**Run container**

docker run -it expense-tracker-cli

**Database**

Uses SQLite (expense_tracker.db)

Models created using SQLAlchemy ORM

Tables: users, categories, budgets, expenses

**Test Steps**

Add Category → Option 1

Set Budget → Option 2

Add Expense → Option 3

Exceed Budget → Add expenses above budget → alert appears

View Monthly Total → Option 4

View Category Summary → Option 5
