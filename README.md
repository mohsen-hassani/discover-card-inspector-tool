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

### 3. Start

```bash
docker compose --env-file .env up -d --build
```

The app will be available at `http://discover-inspector.vione.cloud`.

### 4. Enable HTTPS with Let's Encrypt (recommended)

Install Certbot on the host and obtain a certificate:

```bash
# Stop nginx temporarily to free port 80
docker compose stop nginx

# Obtain certificate (replace with your email)
certbot certonly --standalone \
  -d discover-inspector.vione.cloud \
  --email you@example.com \
  --agree-tos --non-interactive

# Restart
docker compose start nginx
```

Then edit `nginx/nginx.conf`:
1. Uncomment the `return 301 https://...` line in the HTTP server block
2. Uncomment the entire `server { listen 443 ssl ... }` block
3. Uncomment the `/etc/letsencrypt` volume in `docker-compose.yml`
4. Restart: `docker compose restart nginx`

Auto-renewal: add a cron job to run `certbot renew && docker compose restart nginx`.

---

## Data persistence

All uploaded images and the SQLite database are stored in the `card_data` Docker volume at `/data`. Back this up regularly:

```bash
docker run --rm -v discovercardinspectortool_card_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/card_data_backup.tar.gz /data
```
