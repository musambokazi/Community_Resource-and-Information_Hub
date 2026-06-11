from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username=None, password=None, **kwargs):
        super().__init__(username=username, password=password, **kwargs)

class CachedResult(db.Model):
    __tablename__ = 'cached_results'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(255), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    results_json = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, query=None, lat=None, lon=None, results_json=None, timestamp=None, **kwargs):
        super().__init__(
            query=query,
            lat=lat,
            lon=lon,
            results_json=results_json,
            timestamp=timestamp,
            **kwargs
        )

