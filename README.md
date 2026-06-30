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

### 3. Create the data directory on the host

```bash
mkdir -p /opt/discover-inspector/data/uploads
```

### 4. Start the app container

```bash
docker compose --env-file .env up -d --build
```

Gunicorn listens on `127.0.0.1:5001` (host-only, not public). Uploaded files and the database are stored at `/opt/discover-inspector/data/` on the host.

### 5. Configure the host Nginx

```bash
cp nginx/nginx.conf /etc/nginx/sites-available/discover-inspector
ln -s /etc/nginx/sites-available/discover-inspector /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Nginx serves uploaded images directly from `/opt/discover-inspector/data/uploads/` and proxies everything else to Gunicorn.

### 5. Enable HTTPS with Let's Encrypt (recommended)

```bash
certbot --nginx -d discover-inspector.vione.cloud --email you@example.com --agree-tos
```

Certbot will patch the vhost automatically. Auto-renewal runs via the certbot systemd timer (check with `systemctl status certbot.timer`).

---

## Data persistence

All uploaded images and the SQLite database are stored in the `card_data` Docker volume at `/data`. Back this up regularly:

```bash
docker run --rm -v discovercardinspectortool_card_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/card_data_backup.tar.gz /data
```
