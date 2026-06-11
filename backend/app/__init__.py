import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# ── Resolve paths relative to project root ────────────────────────────────────
# backend/app/__init__.py → backend/ → project root
_HERE       = os.path.dirname(os.path.abspath(__file__))   # backend/app/
_BACKEND    = os.path.dirname(_HERE)                        # backend/
_ROOT       = os.path.dirname(_BACKEND)                     # project root
_FRONTEND   = os.path.join(_ROOT, 'frontend')               # project root/frontend/
_TEMPLATES  = os.path.join(_FRONTEND, 'templates')
_STATIC     = os.path.join(_FRONTEND, 'static')


def create_app(config_class=None):
    if config_class is None:
        from config import Config
        config_class = Config

    app = Flask(
        __name__,
        template_folder=_TEMPLATES,
        static_folder=_STATIC,
        static_url_path='/static',
    )
    app.config.from_object(config_class)

    # ── Trust one layer of reverse-proxy headers (nginx → gunicorn) ──────────
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # ── Extensions ────────────────────────────────────────────────────────────
    from app.extensions import db, limiter, talisman, csrf, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    csrf.init_app(app)

    # ── Content Security Policy ───────────────────────────────────────────────
    csp = {
        'default-src': ["'self'"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",
            "https://cdn.tailwindcss.com",
            "https://cdn.jsdelivr.net",
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            "https://fonts.googleapis.com",
            "https://cdn.jsdelivr.net",
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdn.jsdelivr.net",
        ],
        'img-src': [
            "'self'",
            "data:",
            "https://maps.googleapis.com",
            "https://maps.gstatic.com",
            "https://lh3.googleusercontent.com",
        ],
        'connect-src': ["'self'", "https://maps.googleapis.com"],
    }

    is_prod = os.environ.get("FLASK_ENV") == "production"
    talisman.init_app(
        app,
        content_security_policy=csp,
        force_https=is_prod,
        strict_transport_security=is_prod,
        strict_transport_security_max_age=31536000,
        referrer_policy='strict-origin-when-cross-origin',
    )

    # ── Template context processors ───────────────────────────────────────────
    from datetime import datetime

    @app.context_processor
    def inject_globals():
        from flask import session
        from app.models import User
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return {
            'now': datetime.utcnow(),
            'current_user': user,
        }

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.auth import auth as auth_blueprint
    from app.routes.api import api as api_blueprint
    from app.routes.pages import pages as pages_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(pages_blueprint)

    return app
