"""Optional: load demo data for one user so you can take screenshots quickly.
Usage:  python sample_data.py   (then login as demo / demo123)"""
import random

import auth
import database
import transactions

random.seed(7)


def main():
    conn = database.get_connection()
    database.init_db(conn)
    import os
    salt = os.urandom(16).hex()
    try:
        conn.execute("INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                     ("demo", salt, auth._hash("demo123", salt)))
        conn.commit()
    except Exception:
        print("Demo user already exists.")
        return
    uid = conn.execute("SELECT id FROM users WHERE username='demo'").fetchone()["id"]
    cats = {"Food": (2000, 5000), "Rent": (12000, 12000), "Transport": (800, 2500),
            "Utilities": (1000, 2500), "Shopping": (1000, 6000), "Entertainment": (500, 3000)}
    for month in range(1, 10):
        transactions.add(conn, uid, "income", "Salary", 55000, f"2026-{month:02d}-01", "Monthly salary")
        if month % 3 == 0:
            transactions.add(conn, uid, "income", "Freelance", random.randint(5000, 15000), f"2026-{month:02d}-15", "Project")
        for cat, (lo, hi) in cats.items():
            transactions.add(conn, uid, "expense", cat, random.randint(lo, hi), f"2026-{month:02d}-{random.randint(2, 27):02d}", cat)
    print("Demo data loaded. Login with username: demo  password: demo123")


if __name__ == "__main__":
    main()
