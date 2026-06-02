import json
import requests
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, session, jsonify, make_response, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, limiter
from app.models import User, CachedResult

main = Blueprint('main', __name__)

def get_cached(query=None, lat=None, lon=None):
    threshold = datetime.utcnow() - timedelta(hours=24)
    if query:
        res = db.session.query(CachedResult).filter(CachedResult.query == query, CachedResult.timestamp > threshold).first()
    else:
        res = db.session.query(CachedResult).filter(
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

@main.route('/')
@limiter.limit("60 per minute")
def home():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    if not user and not session.get('guest'):
        return redirect('/login')

    return render_template('index.html', user=user)

@main.route('/api/nearby')
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
    
    api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    all_results = []
    for item in search_types:
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&rankby=distance&type={item['type']}&key={api_key}"
        response = requests.get(url).json()

        if "results" in response:
            for place in response["results"][:3]:
                photo_ref = place.get('photos', [{}])[0].get('photo_reference')
                img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}" if photo_ref else "https://via.placeholder.com/400"
                
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

@main.route('/api/search')
@limiter.limit("30 per minute")
def api_search():
    query = request.args.get('q')
    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')
    if not query: return jsonify({"success": False})

    cached = get_cached(query=query)
    if cached: return jsonify({"success": True, "data": cached})

    api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={lat},{lon}&radius=10000&key={api_key}"
    response = requests.get(url).json()
    
    results = []
    if "results" in response:
        for place in response["results"][:12]:
            photo_ref = place.get('photos', [{}])[0].get('photo_reference')
            img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}" if photo_ref else "https://via.placeholder.com/400"
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

@main.route('/login', methods=['GET', 'POST'])
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

@main.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return "Username and password required", 400
    
    existing = User.query.filter_by(username=username).first()
    if existing:
        return "Username already exists", 400
        
    hashed_pwd = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pwd)
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id
    session.pop('guest', None)
    return redirect('/')

@main.route('/guest')
def guest():
    session['guest'] = True
    session.pop('user_id', None)
    return redirect('/')

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/sitemap.xml')
def sitemap():
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
