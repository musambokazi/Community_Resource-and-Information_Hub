import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    if not SECRET_KEY and os.environ.get("FLASK_ENV") == "production":
        raise RuntimeError("FLASK_SECRET_KEY must be set in production")
    SECRET_KEY = SECRET_KEY or "dev-fallback-insecure-key-change-me"

    # ── Session hardening ─────────────────────────────────────────────────────
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://community_hub_user:password123@localhost:5432/community_hub"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── External APIs ─────────────────────────────────────────────────────────
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

    # ── Rate limiting ─────────────────────────────────────────────────────────
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_DEFAULT = "200 per day;60 per minute"

    # ── SEO / Sitemap ─────────────────────────────────────────────────────────
    BASE_URL = os.environ.get("BASE_URL", "https://yourdomain.com")

    # ── WTF / CSRF ────────────────────────────────────────────────────────────
    WTF_CSRF_ENABLED = True
