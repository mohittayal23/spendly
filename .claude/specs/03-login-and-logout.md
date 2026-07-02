# Spec: Login and Logout

## Overview
Implements session-based authentication for existing users. `GET /login` already renders `login.html`, but there is no handler for the submitted form — returning users cannot sign in. `GET /logout` is currently a placeholder stub. This step adds `POST /login` (validating credentials against the `users` table and starting a session) and a real `GET /logout` (tearing down the session). Together with registration (Step 2), this completes the core auth flow that later steps (`profile`, `expenses/*`) depend on for identifying the current user.

## Depends on
- Step 1 (Database setup) — requires `get_db()` and the `users` table with `email`, `password_hash` columns.
- Step 2 (Registration) — requires `app.secret_key` to be set and the session-based auth pattern (`session["user_id"]`) already established by `POST /register`.

## Routes
- `GET /login` — renders the login form — public (already exists, unchanged)
- `POST /login` — validates credentials, starts a session, redirects on success — public
- `GET /logout` — clears the session, redirects to landing — logged-in (safe to call when logged out too; just no-ops)

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) already covers login needs.

## Templates
- **Create:** none
- **Modify:** `templates/login.html` — no structural changes; the existing `{% if error %}` block is reused to surface an invalid-credentials error on re-render

## Files to change
- `app.py`
  - Change `login` view to accept `methods=["GET", "POST"]`
  - On `POST`:
    - Read `email`, `password` from `request.form`
    - Validate both fields are present
    - Look up the user by email (case-insensitive) via a parameterized `SELECT`
    - Verify the password with `check_password_hash` against the stored `password_hash`
    - On missing fields, unknown email, or wrong password: re-render `login.html` with a single generic error (e.g. "Invalid email or password") — do not reveal whether the email exists, to avoid user enumeration
    - On success: set `session["user_id"]` to the user's id, redirect to `/profile`
  - Replace the `logout` stub:
    - Clear `session["user_id"]` (e.g. `session.pop("user_id", None)`)
    - Redirect to `/` (landing)
  - Add `check_password_hash` to the existing `werkzeug.security` import (alongside `generate_password_hash`)

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`check_password_hash` against the existing `pbkdf2:sha256` hashes)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use one generic error message for both "no such user" and "wrong password" — never disclose which one failed
- Never store or log plaintext passwords
- Keep validation server-side even though the form has client-side `required`/`type="email"` attributes — those can be bypassed
- `GET /logout` must work even if no session exists (no crash on missing `user_id`)

## Definition of done
- [ ] Submitting the login form with a valid email/password sets `session["user_id"]` and redirects to `/profile`
- [ ] Submitting with a correct email but wrong password re-renders `login.html` with a generic error and does not set the session
- [ ] Submitting with an email that doesn't exist re-renders `login.html` with the same generic error (not a different one)
- [ ] Submitting with a missing `email` or `password` is rejected with an error, no lookup crash
- [ ] Visiting `/logout` while logged in clears `session["user_id"]` and redirects to `/`
- [ ] Visiting `/logout` while logged out does not error and redirects to `/`
- [ ] `GET /login` still renders the form unchanged
- [ ] App starts and runs with no errors (`python app.py`)
