"""Expense Tracker & Analytics System - entry point."""
from datetime import date

import auth
import charts
import database
import expense
import income
import reports
import validators as v

AUTH_MENU = """
=========================================
   EXPENSE TRACKER & ANALYTICS SYSTEM
=========================================
 1. Register
 2. Login
 3. Exit
"""

USER_MENU = """
-------- MAIN MENU ({user}) --------
 1. Income Management
 2. Expense Management
 3. Monthly Report
 4. Yearly Report
 5. Charts & Visualisations
 6. Export Reports (CSV)
 7. Logout
"""


def ask_year_month(with_month=True):
    today = date.today()
    year = v.get_int(f"Year (Enter = {today.year}): ", 2000, 2100, default=today.year)
    if not with_month:
        return year, None
    month = v.get_int(f"Month 1-12 (Enter = {today.month}): ", 1, 12, default=today.month)
    return year, month


def charts_menu(conn, user):
    print("\n 1. Expense pie chart (month)\n 2. Income vs Expense bar chart (year)\n 3. Savings trend (year)")
    choice = input("Choice: ").strip()
    if choice not in {"1", "2", "3"}:
        print("  ! Invalid choice.")
        return
    year, month = ask_year_month(with_month=(choice == "1"))
    show = input("Open chart window too? (y/n): ").strip().lower() == "y"
    if choice == "1":
        path = charts.expense_pie(conn, user, year, month, show)
    elif choice == "2":
        path = charts.income_vs_expense(conn, user, year, show)
    else:
        path = charts.savings_trend(conn, user, year, show)
    print(f"  Chart saved: {path}" if path else "  No data available for this period.")


def user_session(conn, user):
    while True:
        print(USER_MENU.format(user=user["username"]))
        choice = input("Choice (1-7): ").strip()
        if choice == "1":
            income.menu(conn, user)
        elif choice == "2":
            expense.menu(conn, user)
        elif choice == "3":
            year, month = ask_year_month()
            reports.monthly_report(conn, user["id"], year, month)
        elif choice == "4":
            year, _ = ask_year_month(with_month=False)
            reports.yearly_report(conn, user["id"], year)
        elif choice == "5":
            charts_menu(conn, user)
        elif choice == "6":
            year, _ = ask_year_month(with_month=False)
            for path in reports.export_csv(conn, user, year):
                print(f"  Exported: {path}")
        elif choice == "7":
            print("  Logged out.")
            return
        else:
            print("  ! Invalid choice.")


def main():
    conn = database.get_connection()
    database.init_db(conn)
    try:
        while True:
            print(AUTH_MENU)
            choice = input("Choice (1-3): ").strip()
            if choice == "1":
                auth.register(conn)
            elif choice == "2":
                user = auth.login(conn)
                if user:
                    user_session(conn, user)
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("! Invalid choice.")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting safely. Goodbye!")
    except Exception as err:
        print(f"! Unexpected error: {err}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
