# Discover Card Inspector — CLAUDE.md

## What this project is

A minimal Flask web app for QA inspection of Discover feed cards. Users upload a screenshot and paste the card's JSON payload; the detail view shows them side-by-side with syntax highlighting.

## Architecture

```
app/
  __init__.py   create_app() factory — config, DB init, blueprint registration, Jinja filter
  db.py         SQLite helpers: get_db(), init_db(), close_db(), init_app()
  schema.sql    DDL for users and cards tables
  auth.py       Blueprint: /register /login /logout + login_required decorator
  routes.py     Blueprint: / (gallery) /upload /card/<id> /card/<id>/delete /uploads/<file>
  templates/
    base.html       Tailwind CDN + highlight.js CDN + nav + flash messages
    login.html
    register.html
    gallery.html    Responsive grid; uses from_json Jinja filter to show card title/source
    upload.html     Drag-and-drop image + JSON textarea; client-side image preview
    detail.html     Horizontal thumbnail strip + image panel + JSON panel side-by-side
```

## Key decisions

- **SQLite** — single file at `DATABASE_PATH` env var (default: `instance/db.sqlite3` in dev, `/data/db.sqlite3` in Docker)
- **Images** stored at `UPLOAD_FOLDER` env var, named `<uuid>.<ext>` to avoid collisions
- **JSON** stored as TEXT in SQLite; pretty-printed server-side in `routes.py:card_detail()`
- **highlight.js** (github-dark theme) renders the JSON block in the browser — no build step
- **Tailwind CDN** (play CDN) — no build step; acceptable for an internal tool
- **`from_json` Jinja filter** registered in `__init__.py` — used by gallery to extract title/source from stored JSON
- **Nginx** serves `/uploads/` directly from the Docker volume (bypasses Gunicorn for images)

## Local dev

```bash
pip install flask gunicorn
python main.py          # runs on http://localhost:5000
```

Database and uploads go to `instance/` (created automatically, gitignored).

## Docker

```bash
docker compose up --build
```

Set `SECRET_KEY` via `.env` file or environment variable before deploying to production.

## Adding features

- **Card search/filter**: add a `?q=` param to `routes.py:gallery()` and a `WHERE json_data LIKE` query
- **Pagination**: query with `LIMIT`/`OFFSET`; pass `page` param from the gallery template
- **Multiple images per card**: add a `card_images` table; adjust upload form and detail layout
