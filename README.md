# Discover Card Inspector

A web tool for reviewing Discover feed card screenshots alongside their raw JSON metadata. Upload a screenshot, attach the card's JSON payload, then browse and inspect them side-by-side.

## Features

- Login-protected (register / login / logout)
- Upload a screenshot + paste the card JSON
- Gallery view — responsive grid (2 / 3 / 4 columns)
- Detail view — thumbnail strip, image panel, and syntax-highlighted JSON panel side-by-side
- Delete cards

## Stack

- Python 3.13 + Flask
- SQLite (single-file database)
- Gunicorn (WSGI)
- Nginx (reverse proxy)
- Docker Compose

---

## Quick start (local dev)

```bash
pip install flask gunicorn
python main.py
# open http://localhost:5000
```

---

## Deploy with Docker Compose

### 1. Clone and configure

```bash
git clone <repo>
cd DiscoverCardInspectorTool

# Create a .env file with a strong secret key
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
```

### 2. Point DNS

Create an A record for `discover-inspector.vione.cloud` pointing to your server's IP.

### 3. Create the uploads directory and seed the database file

```bash
mkdir -p uploads
touch db.sqlite3   # must exist as a file before the first `docker compose up`
```

### 4. Start the app container

```bash
docker compose up -d --build
```

Gunicorn listens on `127.0.0.1:5001` (host-only, not public). Files are stored directly in the project root on the host — `uploads/` for images and `db.sqlite3` for the database.

### 5. Configure the host Nginx

Edit `nginx/nginx.conf` and replace `/path/to/DiscoverCardInspectorTool/` with the actual project path (e.g. `/opt/apps/discover-card-inspector-tool/`), then:

```bash
cp nginx/nginx.conf /etc/nginx/sites-available/discover-inspector
ln -s /etc/nginx/sites-available/discover-inspector /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Nginx serves uploaded images directly from `uploads/` in the project root and proxies everything else to Gunicorn.

### 5. Enable HTTPS with Let's Encrypt (recommended)

```bash
certbot --nginx -d discover-inspector.vione.cloud --email you@example.com --agree-tos
```

Certbot will patch the vhost automatically. Auto-renewal runs via the certbot systemd timer (check with `systemctl status certbot.timer`).

---

## Data persistence

Uploaded images and the SQLite database are bind-mounted from the project root on the host — `uploads/` and `db.sqlite3`. Back them up directly:

```bash
tar czf backup-$(date +%F).tar.gz uploads/ db.sqlite3
```
