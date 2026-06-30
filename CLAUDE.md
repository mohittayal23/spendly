# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Spendly** — a Flask expense tracker web app targeting Indian users (amounts in ₹). This is a teaching project; many routes are stubs marked "coming in Step N" that students are meant to implement incrementally.

## Commands

```bash
# Run development server (port 5001)
python app.py

# Run tests
pytest

# Run a single test file
pytest tests/test_auth.py

# Install dependencies (use venv)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Architecture

**Backend**: Single-file Flask app (`app.py`). All routes live here; there are no blueprints yet.

**Database**: SQLite via `database/db.py`. This file is currently a stub — `get_db()`, `init_db()`, and `seed_db()` need to be implemented. The DB file (`expense_tracker.db`) is gitignored. Foreign keys must be enabled explicitly on each connection.

**Templates**: Jinja2 with `templates/base.html` as the shared layout (navbar + footer). Page-specific templates extend it. `base.html` loads `static/css/style.css` globally; landing-specific styles are in `static/css/landing.css` (loaded via `{% block head %}`).

**Frontend**: Vanilla JS in `static/js/main.js` (currently empty — populated as features are built). Page-specific inline scripts go in `{% block scripts %}`.

## Planned route stubs (not yet implemented)

| Route | Purpose |
|---|---|
| `GET /logout` | Session teardown |
| `GET /profile` | User profile page |
| `GET /expenses/add` | Add expense form |
| `GET /expenses/<id>/edit` | Edit expense form |
| `GET /expenses/<id>/delete` | Delete expense |
