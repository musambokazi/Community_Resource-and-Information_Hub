from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import requests
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "community_hub_secret_key_123"

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# YOUR API KEY
API_KEY = "AIzaSyAPNekUGW1nFy1YC5ohKRcKFmblVl15-is"

def get_cached_results(query=None, lat=None, lon=None):
    conn = get_db_connection()
    threshold_time = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    if query:
        res = conn.execute("SELECT results_json FROM cached_results WHERE query = ? AND timestamp > ?", (query, threshold_time)).fetchone()
    else:
        res = conn.execute("SELECT results_json FROM cached_results WHERE ROUND(lat, 3) = ROUND(?, 3) AND ROUND(lon, 3) = ROUND(?, 3) AND query IS NULL AND timestamp > ?", (float(lat), float(lon), threshold_time)).fetchone()
    conn.close()
    return json.loads(res['results_json']) if res else None

def cache_results(results, query=None, lat=None, lon=None):
    conn = get_db_connection()
    conn.execute("INSERT INTO cached_results (query, lat, lon, results_json) VALUES (?, ?, ?, ?)", (query, lat, lon, json.dumps(results)))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    user = None
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()

    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')
    
    cached = get_cached_results(lat=lat, lon=lon)
    if cached:
        return render_template('index.html', items=cached, user=user)

    search_types = [
        {'type': 'police', 'filter': 'police'},
        {'type': 'hospital', 'filter': 'hospital'},
        {'type': 'library', 'filter': 'library'},
        {'type': 'taxi_stand', 'filter': 'transport'}
    ]
    
    all_results = []
    for item in search_types:
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=5000&type={item['type']}&key={API_KEY}"
        response = requests.get(url).json()

        if "results" in response:
            for place in response["results"][:3]:
                photo_ref = place.get('photos', [{}])[0].get('photo_reference')
                img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}" if photo_ref else "https://via.placeholder.com/400"

                # Check opening hours
                is_open = place.get('opening_hours', {}).get('open_now')
                if is_open is True:
                    status = "Open Now"
                    status_class = "status-open"
                elif is_open is False:
                    status = "Closed"
                    status_class = "status-closed"
                else:
                    status = "Hours Unconfirmed (Verify via phone)"
                    status_class = "status-unknown"

                all_results.append({
                    "title": place.get('name'),
                    "category": item['filter'], 
                    "image": img_url,
                    "desc": place.get('vicinity', 'Nearby service'),
                    "lat": place['geometry']['location']['lat'],
                    "lon": place['geometry']['location']['lng'],
                    "status": status,
                    "status_class": status_class,
                    "place_id": place.get('place_id')
                })
    
    cache_results(all_results, lat=lat, lon=lon)
    return render_template('index.html', items=all_results, user=user)

@app.route('/find_specific')
def find_specific():
    user = None
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()

    query = request.args.get('name')
    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')

    cached = get_cached_results(query=query)
    if cached:
        return render_template('index.html', items=cached, user=user)

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={lat},{lon}&radius=10000&key={API_KEY}"
    response = requests.get(url).json()
    
    search_results = []
    if "results" in response:
        for place in response["results"]:
            photo_ref = place.get('photos', [{}])[0].get('photo_reference')
            img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}" if photo_ref else "https://via.placeholder.com/400"
            
            # Check opening hours
            is_open = place.get('opening_hours', {}).get('open_now')
            if is_open is True:
                status = "Open Now"
                status_class = "status-open"
            elif is_open is False:
                status = "Closed"
                status_class = "status-closed"
            else:
                status = "Hours Unconfirmed (Verify via phone)"
                status_class = "status-unknown"

            search_results.append({
                "title": place.get('name'),
                "category": "search-result",
                "image": img_url,
                "desc": place.get('formatted_address'),
                "lat": place['geometry']['location']['lat'],
                "lon": place['geometry']['location']['lng'],
                "status": status,
                "status_class": status_class,
                "place_id": place.get('place_id')
            })
    
    cache_results(search_results, query=query)
    return render_template('index.html', items=search_results, user=user)

@app.route('/details/<place_id>')
def details(place_id):
    user = None
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()

    # Check cache first
    cached = get_cached_results(query=f"details_{place_id}")
    if cached:
        return render_template('details.html', info=cached, user=user)

    fields = "name,rating,formatted_phone_number,opening_hours,geometry,vicinity,formatted_address,website,url,photos,reviews"
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={API_KEY}"
    response = requests.get(url).json()
    
    if "result" in response:
        place = response["result"]
        photos = []
        for p in place.get('photos', [])[:5]:
            ref = p.get('photo_reference')
            photos.append(f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={ref}&key={API_KEY}")
        if not photos: photos = ["https://via.placeholder.com/800"]

        info = {
            "name": place.get('name'),
            "vicinity": place.get('vicinity', place.get('formatted_address')),
            "formatted_phone_number": place.get('formatted_phone_number', 'Not Available'),
            "website": place.get('website'),
            "rating": place.get('rating', 'No rating'),
            "image": photos[0],
            "photos": photos,
            "url": place.get('url'),
            "opening_hours": place.get('opening_hours', {}),
            "weekday_text": place.get('opening_hours', {}).get('weekday_text', []),
            "reviews": place.get('reviews', [])[:3]
        }
        cache_results(info, query=f"details_{place_id}")
        return render_template('details.html', info=info, user=user)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        return "Invalid login"
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_pw))
        conn.commit()
        user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        session['user_id'] = user['id']
        session['username'] = username
    except: return "Username or email already exists"
    finally: conn.close()
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add', methods=['POST'])
def add_resource():
    title = request.form.get('title')
    category = request.form.get('category')
    desc = request.form.get('desc')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    phone = request.form.get('phone')
    if title and category:
        conn = get_db_connection()
        conn.execute("INSERT INTO resources (title, category, desc, lat, lon, phone) VALUES (?, ?, ?, ?, ?, ?)", (title, category, desc, lat, lon, phone))
        conn.commit()
        conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)