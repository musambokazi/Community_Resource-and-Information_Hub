from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username=None, password=None, **kwargs):
        if username is not None:
            kwargs['username'] = username
        if password is not None:
            kwargs['password'] = password
        super().__init__(**kwargs)

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_token = db.Column(db.String(120), nullable=False)
    place_id = db.Column(db.String(120), nullable=False)
    resource_json = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_token=None, place_id=None, resource_json=None, **kwargs):
        if user_token is not None:
            kwargs['user_token'] = user_token
        if place_id is not None:
            kwargs['place_id'] = place_id
        if resource_json is not None:
            kwargs['resource_json'] = resource_json
        super().__init__(**kwargs)

class CachedResult(db.Model):
    __tablename__ = 'cached_results'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(255), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    results_json = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, query=None, lat=None, lon=None, results_json=None, timestamp=None, **kwargs):
        if query is not None:
            kwargs['query'] = query
        if lat is not None:
            kwargs['lat'] = lat
        if lon is not None:
            kwargs['lon'] = lon
        if results_json is not None:
            kwargs['results_json'] = results_json
        if timestamp is not None:
            kwargs['timestamp'] = timestamp
        super().__init__(**kwargs)
