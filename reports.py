"""Monthly and yearly financial reports (console + CSV export)."""
import calendar
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")


def category_totals(conn, user_id, kind, year, month):
    return conn.execute(
        "SELECT category, SUM(amount) AS total FROM transactions "
        "WHERE user_id = ? AND type = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ? "
        "GROUP BY category ORDER BY total DESC",
        (user_id, kind, str(year), f"{month:02d}")).fetchall()


def monthly_totals(conn, user_id, year):
    """Return list of 12 tuples: (month, income, expense, savings)."""
    rows = conn.execute(
        "SELECT CAST(strftime('%m', date) AS INTEGER) AS m, type, SUM(amount) AS total "
        "FROM transactions WHERE user_id = ? AND strftime('%Y', date) = ? GROUP BY m, type",
        (user_id, str(year))).fetchall()
    data = {m: {"income": 0.0, "expense": 0.0} for m in range(1, 13)}
    for r in rows:
        data[r["m"]][r["type"]] = r["total"]
    return [(m, d["income"], d["expense"], d["income"] - d["expense"]) for m, d in data.items()]


def monthly_report(conn, user_id, year, month):
    expenses = category_totals(conn, user_id, "expense", year, month)
    incomes = category_totals(conn, user_id, "income", year, month)
    total_exp = sum(r["total"] for r in expenses)
    total_inc = sum(r["total"] for r in incomes)
    print(f"\n===== MONTHLY REPORT: {calendar.month_name[month]} {year} =====")
    if not expenses and not incomes:
        print("  No transactions for this month.")
        return
    print("\n  Income by category:")
    for r in incomes:
        print(f"   {r['category']:<16}{r['total']:>14,.2f}")
    print("\n  Expenses by category:")
    for r in expenses:
        pct = r["total"] / total_exp * 100 if total_exp else 0
        print(f"   {r['category']:<16}{r['total']:>14,.2f}  ({pct:.1f}%)")
    savings = total_inc - total_exp
    print(f"\n  Total income  : Rs. {total_inc:,.2f}")
    print(f"  Total expense : Rs. {total_exp:,.2f}")
    print(f"  Net savings   : Rs. {savings:,.2f}")
    if total_inc:
        print(f"  Savings rate  : {savings / total_inc * 100:.1f}%")
    if expenses:
        print(f"  Top spending  : {expenses[0]['category']}")


def yearly_report(conn, user_id, year):
    rows = monthly_totals(conn, user_id, year)
    print(f"\n===== YEARLY REPORT: {year} =====")
    print(f"  {'Month':<12}{'Income':>14}{'Expense':>14}{'Savings':>14}")
    print("  " + "-" * 54)
    for m, inc, exp, sav in rows:
        print(f"  {calendar.month_name[m]:<12}{inc:>14,.2f}{exp:>14,.2f}{sav:>14,.2f}")
    ti = sum(r[1] for r in rows)
    te = sum(r[2] for r in rows)
    print("  " + "-" * 54)
    print(f"  {'TOTAL':<12}{ti:>14,.2f}{te:>14,.2f}{ti - te:>14,.2f}")
    active = [r for r in rows if r[2] > 0]
    if active:
        high = max(active, key=lambda r: r[2])
        print(f"\n  Highest spending month: {calendar.month_name[high[0]]} (Rs. {high[2]:,.2f})")
        print(f"  Average monthly expense: Rs. {sum(r[2] for r in active) / len(active):,.2f}")


def export_csv(conn, user, year):
    """Write yearly summary and all transactions of the year to CSV files."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    summary_path = os.path.join(REPORT_DIR, f"{user['username']}_yearly_summary_{year}.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Month", "Income", "Expense", "Savings"])
        for m, inc, exp, sav in monthly_totals(conn, user["id"], year):
            w.writerow([calendar.month_name[m], inc, exp, sav])
    txn_path = os.path.join(REPORT_DIR, f"{user['username']}_transactions_{year}.csv")
    rows = conn.execute(
        "SELECT id, type, category, amount, date, description FROM transactions "
        "WHERE user_id = ? AND strftime('%Y', date) = ? ORDER BY date", (user["id"], str(year))).fetchall()
    with open(txn_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Type", "Category", "Amount", "Date", "Description"])
        w.writerows([tuple(r) for r in rows])
    return summary_path, txn_path
