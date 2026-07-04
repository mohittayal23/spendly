import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

with app.app_context():
    init_db()
    seed_db()


@app.context_processor
def inject_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return {"current_user": None}

    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return {"current_user": user}


@app.template_filter("inr")
def format_inr(value):
    return f"{value:,.0f}"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = None
        if not name or not email or not password:
            error = "All fields are required."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif "@" not in email or email.count("@") != 1:
            error = "Please enter a valid email address."

        if error:
            return render_template("register.html", error=error)

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,)
        ).fetchone()
        if existing:
            conn.close()
            return render_template(
                "register.html", error="An account with this email already exists."
            )

        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        try:
            with conn:
                cur = conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, password_hash),
                )
                new_user_id = cur.lastrowid
        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                "register.html", error="An account with this email already exists."
            )

        conn.close()
        session["user_id"] = new_user_id
        return redirect(url_for("landing"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = "Invalid email or password."

        if not email or not password:
            return render_template("login.html", error=error)

        conn = get_db()
        user = conn.execute(
            "SELECT id, password_hash FROM users WHERE LOWER(email) = LOWER(?)", (email,)
        ).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error=error)

        session["user_id"] = user["id"]
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("landing"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    totals = conn.execute(
        "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    category_rows = conn.execute(
        "SELECT category, COALESCE(SUM(amount), 0) AS total FROM expenses "
        "WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,),
    ).fetchall()
    recent_rows = conn.execute(
        "SELECT amount, category, date, description FROM expenses "
        "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 5",
        (user_id,),
    ).fetchall()
    conn.close()

    avg_amount = totals["total"] / totals["count"] if totals["count"] else 0
    member_since = datetime.strptime(
        user["created_at"], "%Y-%m-%d %H:%M:%S"
    ).strftime("%b %Y")
    avatar_letter = user["name"][0].upper() if user["name"] else "?"

    max_total = max((row["total"] for row in category_rows), default=0)
    categories = [
        {
            "category": row["category"],
            "total": row["total"],
            "width_pct": round(row["total"] / max_total * 100) if max_total else 0,
        }
        for row in category_rows
    ]
    recent = [
        {
            "date_display": datetime.strptime(row["date"], "%Y-%m-%d").strftime("%b %d"),
            "category": row["category"],
            "description": row["description"],
            "amount": row["amount"],
        }
        for row in recent_rows
    ]

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        avatar_letter=avatar_letter,
        total_count=totals["count"],
        total_amount=totals["total"],
        avg_amount=avg_amount,
        categories=categories,
        recent=recent,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
