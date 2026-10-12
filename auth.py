"""User registration and login (salted PBKDF2 password hashing)."""
import getpass
import hashlib
import hmac
import os
import sqlite3

import validators as v

ITERATIONS = 100_000


def _hash(password, salt_hex):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS).hex()


def register(conn):
    print("\n--- Register ---")
    username = input("Choose username (3-20 letters/digits/_): ").strip()
    if not v.valid_username(username):
        print("  ! Invalid username.")
        return False
    password = getpass.getpass("Choose password (min 6 chars, letters + digits): ")
    if not v.valid_password(password):
        print("  ! Weak password. Use at least 6 characters with letters and digits.")
        return False
    if password != getpass.getpass("Confirm password: "):
        print("  ! Passwords do not match.")
        return False
    salt = os.urandom(16).hex()
    try:
        conn.execute("INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                     (username, salt, _hash(password, salt)))
        conn.commit()
    except sqlite3.IntegrityError:
        print("  ! Username already taken.")
        return False
    print("  Registration successful. You can log in now.")
    return True


def login(conn, max_attempts=3):
    print("\n--- Login ---")
    username = input("Username: ").strip()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    for attempt in range(1, max_attempts + 1):
        password = getpass.getpass("Password: ")
        if row and hmac.compare_digest(_hash(password, row["salt"]), row["password_hash"]):
            print(f"  Welcome, {row['username']}!")
            return {"id": row["id"], "username": row["username"]}
        print(f"  ! Invalid credentials ({attempt}/{max_attempts}).")
    print("  Too many failed attempts.")
    return None
