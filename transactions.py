"""Shared CRUD logic for income and expense records."""
import validators as v

UPDATABLE = {"category", "amount", "date", "description"}


def add(conn, user_id, kind, category, amount, date, description=""):
    cur = conn.execute(
        "INSERT INTO transactions (user_id, type, category, amount, date, description) "
        "VALUES (?, ?, ?, ?, ?, ?)", (user_id, kind, category, amount, date, description))
    conn.commit()
    return cur.lastrowid


def list_all(conn, user_id, kind, limit=50):
    return conn.execute(
        "SELECT * FROM transactions WHERE user_id = ? AND type = ? "
        "ORDER BY date DESC, id DESC LIMIT ?", (user_id, kind, limit)).fetchall()


def get(conn, user_id, kind, tid):
    return conn.execute("SELECT * FROM transactions WHERE id = ? AND user_id = ? AND type = ?",
                        (tid, user_id, kind)).fetchone()


def update(conn, user_id, kind, tid, **fields):
    fields = {k: val for k, val in fields.items() if k in UPDATABLE and val is not None}
    if not fields:
        return False
    assignments = ", ".join(f"{k} = ?" for k in fields)
    cur = conn.execute(
        f"UPDATE transactions SET {assignments} WHERE id = ? AND user_id = ? AND type = ?",
        (*fields.values(), tid, user_id, kind))
    conn.commit()
    return cur.rowcount > 0


def delete(conn, user_id, kind, tid):
    cur = conn.execute("DELETE FROM transactions WHERE id = ? AND user_id = ? AND type = ?",
                       (tid, user_id, kind))
    conn.commit()
    return cur.rowcount > 0


def _show(rows, kind):
    if not rows:
        print(f"  No {kind} records found.")
        return
    print(f"\n  {'ID':<5}{'Date':<12}{'Category':<16}{'Amount':>12}  Description")
    print("  " + "-" * 62)
    for r in rows:
        print(f"  {r['id']:<5}{r['date']:<12}{r['category']:<16}{r['amount']:>12,.2f}  {r['description']}")


def ledger_menu(conn, user, kind, categories):
    """Menu used by both income.py and expense.py."""
    title = kind.capitalize()
    while True:
        print(f"\n--- {title} Management ---")
        print(" 1. Add   2. View   3. Update   4. Delete   5. Back")
        choice = input("Choice: ").strip()
        if choice == "1":
            category = v.get_category(categories)
            amount = v.get_amount("  Amount (Rs.): ")
            date = v.get_date("  Date YYYY-MM-DD (Enter = today): ")
            desc = v.get_text("  Description (optional): ", allow_blank=True)
            tid = add(conn, user["id"], kind, category, amount, date, desc)
            print(f"  {title} added (ID {tid}).")
        elif choice == "2":
            _show(list_all(conn, user["id"], kind), kind)
        elif choice == "3":
            tid = v.get_int("  Record ID to update: ", 1, 10**9)
            if not get(conn, user["id"], kind, tid):
                print("  ! Record not found.")
                continue
            print("  (Press Enter to keep current value)")
            category = v.get_category(categories, allow_blank=True)
            amount = v.get_amount("  New amount: ", allow_blank=True)
            date = v.get_date("  New date: ", allow_blank=True)
            desc = v.get_text("  New description: ", allow_blank=True)
            ok = update(conn, user["id"], kind, tid, category=category, amount=amount,
                        date=date, description=desc or None)
            print("  Updated." if ok else "  Nothing changed.")
        elif choice == "4":
            tid = v.get_int("  Record ID to delete: ", 1, 10**9)
            if not get(conn, user["id"], kind, tid):
                print("  ! Record not found.")
            elif input("  Confirm delete (y/n): ").strip().lower() == "y":
                delete(conn, user["id"], kind, tid)
                print("  Deleted.")
        elif choice == "5":
            return
        else:
            print("  ! Invalid choice.")
