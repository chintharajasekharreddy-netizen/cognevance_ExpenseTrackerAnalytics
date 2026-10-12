"""Matplotlib visualisations. Charts are saved as PNG files in /charts."""
import calendar
import os

import matplotlib.pyplot as plt

import reports

CHART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")


def _finish(fig, filename, show):
    os.makedirs(CHART_DIR, exist_ok=True)
    path = os.path.join(CHART_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    if show:
        plt.show()
    plt.close(fig)
    return path


def expense_pie(conn, user, year, month, show=False):
    rows = reports.category_totals(conn, user["id"], "expense", year, month)
    if not rows:
        return None
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.pie([r["total"] for r in rows], labels=[r["category"] for r in rows],
           autopct="%1.1f%%", startangle=140)
    ax.set_title(f"Expense Breakdown - {calendar.month_name[month]} {year}")
    return _finish(fig, f"{user['username']}_expense_pie_{year}_{month:02d}.png", show)


def income_vs_expense(conn, user, year, show=False):
    data = reports.monthly_totals(conn, user["id"], year)
    if not any(r[1] or r[2] for r in data):
        return None
    labels = [calendar.month_abbr[r[0]] for r in data]
    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - 0.2 for i in x], [r[1] for r in data], width=0.4, label="Income", color="#2e7d32")
    ax.bar([i + 0.2 for i in x], [r[2] for r in data], width=0.4, label="Expense", color="#c62828")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Amount (Rs.)")
    ax.set_title(f"Income vs Expense - {year}")
    ax.legend()
    return _finish(fig, f"{user['username']}_income_vs_expense_{year}.png", show)


def savings_trend(conn, user, year, show=False):
    data = reports.monthly_totals(conn, user["id"], year)
    if not any(r[1] or r[2] for r in data):
        return None
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot([calendar.month_abbr[r[0]] for r in data], [r[3] for r in data],
            marker="o", color="#1565c0")
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.set_ylabel("Savings (Rs.)")
    ax.set_title(f"Monthly Savings Trend - {year}")
    ax.grid(alpha=0.3)
    return _finish(fig, f"{user['username']}_savings_trend_{year}.png", show)
