import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "expense_tracker.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    DEFAULT (datetime('now'))
            );
        """)
    conn.close()


def seed_db():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        conn.close()
        return

    with conn:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123", method="pbkdf2:sha256")),
        )
        user = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
        ).fetchone()

        sample_expenses = [
            (user["id"], 1250.00, "Food",          "2026-06-01", "Big Bazaar groceries"),
            (user["id"],  500.00, "Transport",     "2026-06-03", "Metro recharge"),
            (user["id"],  649.00, "Entertainment", "2026-06-05", "Netflix monthly"),
            (user["id"], 1800.00, "Bills",         "2026-06-10", "Electricity bill"),
            (user["id"],  980.00, "Food",          "2026-06-15", "Anniversary dinner"),
            (user["id"], 2500.00, "Shopping",      "2026-06-18", "Myntra order"),
            (user["id"],  450.00, "Health",        "2026-06-21", "Pharmacy"),
            (user["id"],  300.00, "Other",         "2026-06-25", "Misc expense"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            sample_expenses,
        )
    conn.close()
