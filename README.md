# Community Resource & Information Hub

> **Find essential community services — hospitals, police stations, schools, and transport — with real-time operating hours and one-tap directions.**

A production-ready Flask web application serving communities in South Africa with location-aware resource discovery powered by the Google Places API.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
  - [Docker (Production)](#docker-production)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)

---

## Features

- 📍 **Location-aware search** — find services near your current GPS position
- 🏥 **Category filters** — hospitals, police, schools, transport
- 🕐 **Live status** — real-time open/closed indicators from Google Places
- 🗺️ **One-tap directions** — deep-links to Google Maps navigation
- ⚡ **Smart caching** — 24-hour DB-level cache to reduce API costs
- 🔐 **Auth** — username/password accounts + guest access
- 📱 **PWA** — installable, offline-capable via service worker
- 🔒 **Security** — CSRF protection, rate limiting, HTTPS enforcement, CSP headers

---

## Project Structure

```
Community_Resource-and-Information_Hub/
│
├── backend/                        # Flask application (Python)
│   ├── app/
│   │   ├── __init__.py             # App factory — creates Flask app
│   │   ├── extensions.py           # Flask extensions (db, limiter, csrf, migrate)
│   │   ├── models.py               # SQLAlchemy models (User, CachedResult)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py             # /login  /signup  /logout  /guest
│   │       ├── api.py              # /api/nearby  /api/search  /api/health
│   │       └── pages.py            # /  /terms  /privacy  /sitemap.xml
│   ├── migrations/                 # Flask-Migrate / Alembic auto-generated
│   ├── tests/
│   │   └── test_app.py             # pytest suite (8 tests)
│   ├── config.py                   # Config class (reads env vars)
│   ├── gunicorn.conf.py            # Gunicorn WSGI server config
│   ├── pytest.ini                  # Test runner config
│   ├── requirements.txt            # Python dependencies
│   └── run.py                      # Development entry point
│
├── frontend/                       # Static assets & Jinja2 templates
│   ├── static/
│   │   ├── style.css               # Custom CSS (animations, glass cards)
│   │   ├── script.js               # Shared JS utilities
│   │   ├── sw.js                   # Service worker (PWA offline support)
│   │   └── manifest.json           # Web app manifest
│   └── templates/
│       ├── base.html               # Base layout (SEO, OG tags, nav, footer)
│       ├── index.html              # Home — search + results grid
│       ├── login.html              # Auth — login + signup tabs
│       ├── details.html            # Resource detail view
│       ├── terms.html              # Terms of Service
│       └── privacy.html            # Privacy Policy
│
├── nginx/
│   └── community_hub.conf          # Nginx reverse-proxy + TLS config
│
├── logs/                           # Runtime logs (gitignored)
│
├── .dockerignore
├── .env.example                    # Required environment variables template
├── .gitignore
├── docker-compose.yml              # Full stack: web + nginx + postgres + redis
├── Dockerfile                      # Multi-stage production image
├── robots.txt                      # Crawler directives
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Flask 3.x |
| **Database** | PostgreSQL (prod) / SQLite (dev) via SQLAlchemy |
| **Migrations** | Flask-Migrate (Alembic) |
| **Auth** | Werkzeug password hashing + Flask sessions |
| **CSRF** | Flask-WTF |
| **Rate Limiting** | Flask-Limiter + Redis |
| **Security Headers** | Flask-Talisman (CSP, HSTS, HTTPS) |
| **WSGI Server** | Gunicorn |
| **Reverse Proxy** | Nginx |
| **Containerisation** | Docker + Docker Compose |
| **External API** | Google Places API (Nearby Search + Text Search) |
| **Frontend** | Jinja2 templates + Tailwind CSS (CDN) + Vanilla JS |
| **PWA** | Service Worker + Web App Manifest |

---

## Getting Started

### Prerequisites

- Python 3.11+
- A [Google Maps Platform](https://console.cloud.google.com/) project with **Places API** enabled
- Redis (optional for dev — falls back to in-memory)

### Local Development

```bash
# 1. Clone
git clone https://github.com/musambokazi/Community_Resource-and-Information_Hub.git
cd Community_Resource-and-Information_Hub

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — at minimum set FLASK_SECRET_KEY and GOOGLE_MAPS_API_KEY

# 5. Initialise the database
cd backend
flask --app run:app db upgrade

# 6. Run
python run.py
# → http://localhost:5000
```

### Docker (Production)

```bash
# 1. Copy and fill in your environment
cp .env.example .env

# 2. Build and start all services
docker compose up -d --build

# 3. Run migrations inside the container
docker compose exec web flask --app run:app db upgrade

# Services:
#   nginx  → :80 (HTTP → HTTPS redirect) / :443 (HTTPS)
#   web    → :8000 (internal, via nginx)
#   db     → PostgreSQL (internal)
#   redis  → Redis (internal)
```

---

## Environment Variables

Copy `.env.example` to `.env` and set the following:

| Variable | Description | Required |
|---|---|---|
| `FLASK_ENV` | `production` or `development` | Yes |
| `FLASK_SECRET_KEY` | Random hex string — `python -c "import secrets; print(secrets.token_hex(32))"` | Yes |
| `GOOGLE_MAPS_API_KEY` | Google Places API key (restrict to your server IP in prod) | Yes |
| `DATABASE_URL` | PostgreSQL URI — `postgresql://user:pass@host:5432/db` | Yes (prod) |
| `DB_NAME` | Database name for Docker Compose | Yes (Docker) |
| `DB_USER` | Database user for Docker Compose | Yes (Docker) |
| `DB_PASSWORD` | Database password for Docker Compose | Yes (Docker) |
| `REDIS_URL` | Redis connection URI — `redis://localhost:6379` | Recommended |
| `BASE_URL` | Your public domain — `https://yourdomain.com` | Yes (prod) |

---

## Database Migrations

This project uses **Flask-Migrate** (Alembic). Never use `db.create_all()` in production.

```bash
cd backend

# First-time setup
flask --app run:app db init

# After changing models
flask --app run:app db migrate -m "describe your change"
flask --app run:app db upgrade

# Rollback one version
flask --app run:app db downgrade
```

---

## Testing

```bash
cd backend
python -m pytest -v
```

The test suite covers:

| Test | What it verifies |
|---|---|
| `test_database_integrity` | SQLAlchemy tables exist |
| `test_home_redirects_to_login` | Unauthenticated users redirected |
| `test_health_endpoint` | `/api/health` returns 200 |
| `test_api_nearby_with_mock` | Nearby API maps Google response correctly |
| `test_api_search_requires_query` | Returns 400 when `q` is missing |
| `test_caching_logic` | Pre-cached results returned without API call |
| `test_login_page_renders` | Login page returns 200 |
| `test_signup_validates_password_length` | Short passwords rejected |
| `test_sitemap_xml` | Sitemap returns valid XML |

---

## API Reference

All API endpoints are under `/api/`.

### `GET /api/health`
Liveness probe for Docker and load balancers.
```json
{ "status": "ok" }
```

### `GET /api/nearby`
Returns up to 12 nearby community services using GPS coordinates.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `lat` | float | -26.2500 | Latitude |
| `lon` | float | 28.4333 | Longitude |

**Rate limit:** 20 requests/minute per IP

```json
{
  "success": true,
  "cached": false,
  "data": [
    {
      "title": "Johannesburg General Hospital",
      "category": "hospital",
      "image": "https://...",
      "desc": "York Rd, Park Town",
      "lat": -26.1889,
      "lon": 28.0436,
      "is_open": true,
      "place_id": "ChIJ..."
    }
  ]
}
```

### `GET /api/search`
Text search for community services.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `q` | string | ✅ | Search query |
| `lat` | float | | Location bias latitude |
| `lon` | float | | Location bias longitude |

**Rate limit:** 30 requests/minute per IP

---

## Deployment

### Bare-metal (Ubuntu/Debian)

```bash
# Install Nginx, Certbot, Redis
sudo apt install nginx redis-server certbot python3-certbot-nginx

# SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Update nginx config
sudo cp nginx/community_hub.conf /etc/nginx/sites-available/community_hub
# Edit: replace yourdomain.com and web:8000 → 127.0.0.1:8000
sudo ln -s /etc/nginx/sites-available/community_hub /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Run with gunicorn (from backend/)
cd /var/www/community_hub/backend
gunicorn --config gunicorn.conf.py run:app
```

### Docker (Recommended)

See [Docker (Production)](#docker-production) above.

---

## Security

| Control | Implementation |
|---|---|
| CSRF Protection | Flask-WTF on all POST forms |
| Rate Limiting | Flask-Limiter (Redis-backed) + Nginx `limit_req` |
| HTTPS | Enforced via Nginx redirect + Talisman HSTS |
| Secure Cookies | `SECURE`, `HTTPONLY`, `SAMESITE=Lax` |
| Content Security Policy | Talisman CSP — restricts script/style/image sources |
| SQL Injection | SQLAlchemy ORM — parameterised queries only |
| XSS | `escHtml()` on all API data rendered via `innerHTML` |
| Secret Management | All secrets via environment variables — never hardcoded |
| Non-root Docker | App runs as `appuser` (UID 1000) |
| Proxy Trust | `ProxyFix` middleware — rate limiting uses real client IP |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## License

MIT © 2026 Community Hub. Built for Impact.