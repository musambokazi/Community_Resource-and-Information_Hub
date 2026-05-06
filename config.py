import os

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "fallback_secret_key_for_dev")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///community.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
