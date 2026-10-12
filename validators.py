"""Input validation helpers."""
import re
from datetime import date, datetime


def get_text(prompt, allow_blank=False, max_len=100):
    while True:
        value = input(prompt).strip()
        if (value or allow_blank) and len(value) <= max_len:
            return value
        print("  ! Invalid input (cannot be empty / too long).")


def get_int(prompt, minimum, maximum, default=None):
    """Integer in range. If default is given, pressing Enter returns it."""
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            number = int(raw)
        except ValueError:
            print("  ! Please enter a whole number.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"  ! Value must be between {minimum} and {maximum}.")


def get_amount(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip().replace(",", "")
        if not raw and allow_blank:
            return None
        try:
            amount = round(float(raw), 2)
        except ValueError:
            print("  ! Please enter a valid number.")
            continue
        if 0 < amount <= 100_000_000:
            return amount
        print("  ! Amount must be greater than 0.")


def get_date(prompt, allow_blank=False):
    """Date as YYYY-MM-DD. Enter = today (add) or keep (update, allow_blank)."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            return None if allow_blank else date.today().isoformat()
        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("  ! Use format YYYY-MM-DD (e.g. 2026-10-12).")
            continue
        if parsed > date.today():
            print("  ! Date cannot be in the future.")
            continue
        return parsed.isoformat()


def get_category(categories, allow_blank=False):
    for i, name in enumerate(categories, 1):
        print(f"   {i}. {name}")
    while True:
        raw = input("  Choose category number: ").strip()
        if not raw and allow_blank:
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(categories):
            return categories[int(raw) - 1]
        print("  ! Invalid category number.")


def valid_username(name):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", name))


def valid_password(pw):
    return len(pw) >= 6 and any(c.isdigit() for c in pw) and any(c.isalpha() for c in pw)
