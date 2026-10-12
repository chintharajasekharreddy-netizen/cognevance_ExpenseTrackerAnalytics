
"""Income management module."""
import transactions

CATEGORIES = ["Salary", "Business", "Freelance", "Investment", "Gift", "Other"]


def menu(conn, user):
    transactions.ledger_menu(conn, user, "income", CATEGORIES)
