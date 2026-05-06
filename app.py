import os
import json
import math
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from werkzeug.security import generate_password_hash, check_password_hash

# Extensions
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class CachedResult(db.Model):
    __tablename__ = 'cached_results'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(255), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    results_json = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def create_app():
    # Load .env file manually
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback_secret_key_for_dev")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///community.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extensions
    db.init_app(app)
    limiter.init_app(app)
    
    # Configure Talisman (Content Security Policy for CDN)
    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com", "https://cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https://maps.googleapis.com", "https://via.placeholder.com", "https://i.pravatar.cc"],
        'connect-src': ["'self'", "https://maps.googleapis.com"]
    }
    talisman.init_app(app, content_security_policy=csp, force_https=False) # force_https=False for local dev

    with app.app_context():
        db.create_all()

    API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

    def get_cached(query=None, lat=None, lon=None):
        threshold = datetime.utcnow() - timedelta(hours=24)
        if query:
            res = CachedResult.query.filter(CachedResult.query == query, CachedResult.timestamp > threshold).first()
        else:
            # Simple approximation for lat/lon caching (rounded to 3 decimal places)
            res = CachedResult.query.filter(
                db.func.round(CachedResult.lat, 3) == round(float(lat), 3),
                db.func.round(CachedResult.lon, 3) == round(float(lon), 3),
                CachedResult.query == None,
                CachedResult.timestamp > threshold
            ).first()
        return json.loads(res.results_json) if res else None

    def save_cache(results, query=None, lat=None, lon=None):
        cache = CachedResult(query=query, lat=lat, lon=lon, results_json=json.dumps(results))
        db.session.add(cache)
        db.session.commit()

    # Routes
    @app.route('/')
    @limiter.limit("60 per minute")
    def home():
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])

        if not user and not session.get('guest'):
            return redirect('/login')

        return render_template('index.html', user=user)

    @app.route('/api/nearby')
    def api_nearby():
        lat = request.args.get('lat', '-26.2500')
        lon = request.args.get('lon', '28.4333')
        
        cached = get_cached(lat=lat, lon=lon)
        if cached: return jsonify({"success": True, "data": cached})

        search_types = [
            {'type': 'police', 'filter': 'police'},
            {'type': 'hospital', 'filter': 'hospital'},
            {'type': 'school', 'filter': 'education'},
            {'type': 'taxi_stand', 'filter': 'transport'}
        ]
        
        all_results = []
        for item in search_types:
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&rankby=distance&type={item['type']}&key={API_KEY}"
            response = requests.get(url).json()

            if "results" in response:
                for place in response["results"][:3]:
                    photo_ref = place.get('photos', [{}])[0].get('photo_reference')
                    img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}" if photo_ref else "https://via.placeholder.com/400"
                    
                    all_results.append({
                        "title": place.get('name'),
                        "category": item['filter'], 
                        "image": img_url,
                        "desc": place.get('vicinity', 'Nearby service'),
                        "lat": place['geometry']['location']['lat'],
                        "lon": place['geometry']['location']['lng'],
                        "is_open": place.get('opening_hours', {}).get('open_now'),
                        "place_id": place.get('place_id')
                    })
        
        save_cache(all_results, lat=lat, lon=lon)
        return jsonify({"success": True, "data": all_results})

    @app.route('/api/search')
    @limiter.limit("30 per minute")
    def api_search():
        query = request.args.get('q')
        lat = request.args.get('lat', '-26.2500')
        lon = request.args.get('lon', '28.4333')
        if not query: return jsonify({"success": False})

        cached = get_cached(query=query)
        if cached: return jsonify({"success": True, "data": cached})

        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={lat},{lon}&radius=10000&key={API_KEY}"
        response = requests.get(url).json()
        
        results = []
        if "results" in response:
            for place in response["results"][:12]:
                photo_ref = place.get('photos', [{}])[0].get('photo_reference')
                img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}" if photo_ref else "https://via.placeholder.com/400"
                results.append({
                    "title": place.get('name'),
                    "category": "search-result",
                    "image": img_url,
                    "desc": place.get('formatted_address'),
                    "lat": place['geometry']['location']['lat'],
                    "lon": place['geometry']['location']['lng'],
                    "is_open": place.get('opening_hours', {}).get('open_now'),
                    "place_id": place.get('place_id')
                })
        
        save_cache(results, query=query)
        return jsonify({"success": True, "data": results})

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            if 'guest' in request.form:
                session['guest'] = True
                return redirect('/')
            
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session.pop('guest', None)
                return redirect('/')
            return "Invalid credentials", 401
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/login')

    @app.route('/terms')
    def terms():
        return render_template('terms.html')

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html')

    @app.route('/sitemap.xml')
    def sitemap():
        """Dynamic Sitemap Generation"""
        pages = [
            {"url": "/", "priority": 1.0},
            {"url": "/terms", "priority": 0.5},
            {"url": "/privacy", "priority": 0.5}
        ]
        
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for page in pages:
            sitemap_xml += f"  <url>\n    <loc>https://yourdomain.com{page['url']}</loc>\n    <priority>{page['priority']}</priority>\n  </url>\n"
        sitemap_xml += "</urlset>"
        
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')