"""Expense management module."""
import transactions

CATEGORIES = ["Food", "Rent", "Transport", "Utilities", "Shopping",
              "Health", "Education", "Entertainment", "Other"]


def menu(conn, user):
    transactions.ledger_menu(conn, user, "expense", CATEGORIES)
