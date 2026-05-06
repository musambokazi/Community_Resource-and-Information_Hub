from flask import Flask
from config import Config
from app.extensions import db, limiter, talisman

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    limiter.init_app(app)
    
    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com", "https://cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https://maps.googleapis.com", "https://via.placeholder.com", "https://i.pravatar.cc"],
        'connect-src': ["'self'", "https://maps.googleapis.com"]
    }
    talisman.init_app(app, content_security_policy=csp, force_https=False) # force_https=False for local dev

    # Register blueprints here
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()

    return app
