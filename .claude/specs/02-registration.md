# Spec: Registration

## Overview
Implements account creation for Spendly. `GET /register` already renders `register.html`, but there is no handler for the submitted form — the app cannot create users yet. This step adds `POST /register`, wiring the existing form to `database/db.py`'s `users` table: validating input, hashing the password, inserting the row, and starting a logged-in session. This is the first step that introduces session-based auth, which later steps (`logout`, `profile`) depend on.

## Depends on
- Step 1 (Database setup) — requires `get_db()`, `init_db()`, and the `users` table with `name`, `email`, `password_hash` columns.

## Routes
- `GET /register` — renders the registration form — public (already exists, unchanged)
- `POST /register` — validates input, creates the user, starts a session, redirects on success — public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) already covers registration needs.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — no structural changes; the existing `{% if error %}` block is reused to surface validation/duplicate-email errors on re-render

## Files to change
- `app.py`
  - Add `app.secret_key` (from an env var, e.g. `os.environ.get("SECRET_KEY", "dev")`) so `session` can be used
  - Add imports: `request`, `redirect`, `url_for`, `session` from `flask`; `generate_password_hash` from `werkzeug.security`; `get_db` (already imported)
  - Change `register` view to accept `methods=["GET", "POST"]`
  - On `POST`:
    - Read `name`, `email`, `password` from `request.form`
    - Validate all fields are present, `password` is at least 8 characters, and `email` looks well-formed
    - Check for an existing user with the same email (case-insensitive) via a parameterized `SELECT`
    - On validation failure or duplicate email, re-render `register.html` with an `error` message (200, form not cleared server-side)
    - On success: hash the password with `generate_password_hash(password, method="pbkdf2:sha256")`, insert the user, set `session["user_id"]` to the new user's id, redirect to `/profile`

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`, `pbkdf2:sha256`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Email uniqueness check and insert must not race — rely on the existing `UNIQUE` constraint on `users.email` as the source of truth; catch `sqlite3.IntegrityError` as a fallback if the pre-check passes but the insert still collides
- Never store or log plaintext passwords
- Keep validation server-side even though the form has client-side `required`/`type="email"` attributes — those can be bypassed

## Definition of done
- [ ] Submitting the register form with valid, unique details creates a row in `users` with a hashed (not plaintext) password
- [ ] After successful registration, the browser is redirected to `/profile` and `session["user_id"]` is set (visible via a logged Flask session or a temporary debug check)
- [ ] Submitting with an email that already exists in `users` re-renders `register.html` with an error and does not insert a duplicate row
- [ ] Submitting with a password under 8 characters is rejected server-side with an error, even if client-side validation is bypassed (e.g. via curl/Postman)
- [ ] Submitting with a missing `name`, `email`, or `password` is rejected with an error and no row is inserted
- [ ] `GET /register` still renders the form unchanged
- [ ] App starts and runs with no errors (`python app.py`)
