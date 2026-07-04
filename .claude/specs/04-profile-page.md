# Spec: Profile Page

## Overview
Implements the real `GET /profile` page, replacing the `"Profile page — coming in Step 4"` stub. This is the first page in Spendly that requires the user to be logged in — visiting it while logged out must redirect to `/login`. The page shows the signed-in user's account details (name, email, member-since date) alongside a read-only summary of their expense activity (total spent, expense count, per-category breakdown, and a short list of recent expenses), pulled from the `expenses` table that Step 1 already seeds with demo data. No expense creation/editing happens here — that's Steps 7-9.

## Depends on
- Step 1 (Database setup) — requires `get_db()` and the `users`/`expenses` tables.
- Step 2 (Registration) and Step 3 (Login and Logout) — requires `session["user_id"]` to already be set by a successful login/registration, and establishes the login-required pattern this step introduces as a reusable check.

## Routes
- `GET /profile` — renders the current user's profile and expense summary — logged-in only (redirects to `GET /login` if no `session["user_id"]`)

## Database changes
No database changes. Uses the existing `users` table (`id`, `name`, `email`, `created_at`) and `expenses` table (`user_id`, `amount`, `category`, `date`, `description`) as defined in `database/db.py`. All queries are `SELECT`s — no schema changes needed.

## Templates
- **Create:** `templates/profile.html` — profile header (name, email, member-since), a stats row (total spent, number of expenses), a per-category breakdown list, and a "recent expenses" list (most recent 5 by `date` then `id`)
- **Modify:** none

## Files to change
- `app.py`
  - Replace the `profile` stub with a real view:
    - If `session.get("user_id")` is missing, `redirect(url_for("login"))`
    - Otherwise, fetch the user row (`id`, `name`, `email`, `created_at`) via a parameterized `SELECT ... WHERE id = ?`
    - Fetch aggregate totals: `SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?`
    - Fetch per-category totals: `SELECT category, COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC`
    - Fetch the 5 most recent expenses: `SELECT amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 5`
    - Close the connection and render `profile.html` with the user, totals, category breakdown, and recent expenses
- `static/css/style.css`
  - Add a `.profile-section` / `.profile-container` block (mirroring the existing `.auth-section` / `.auth-container` pattern) plus new classes for the stats row and category breakdown (e.g. `.profile-stats`, `.stat-card`, `.category-list`, `.category-row`, `.recent-list`). All colors via existing `--ink*`, `--accent*`, `--border*`, `--paper*` variables — no new hex values unless added to `:root` first.

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (not touched in this step, but existing hashes must not be read/exposed on the profile page)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Never display `password_hash` in the template or pass it into the render context
- Login-required check must happen before any database query runs
- Handle a user with zero expenses gracefully (show "₹0" totals and an empty state message, not an error)
- Format currency with the ₹ symbol, matching the existing landing page mock card style (`.mock-total`, `.mock-amt`)

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Visiting `/profile` while logged in (demo user) shows the correct name and email
- [ ] Total spent and expense count match the sum/count of the demo user's 8 seeded expenses
- [ ] Per-category breakdown lists each category present in the demo data with correct subtotals
- [ ] Recent expenses list shows at most 5 items, most recent first
- [ ] A newly registered user with no expenses sees a "₹0" / empty state instead of an error
- [ ] `password_hash` never appears in the rendered HTML (view page source to confirm)
- [ ] App starts and runs with no errors (`python app.py`)
