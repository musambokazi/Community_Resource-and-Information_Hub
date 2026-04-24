from flask import Flask, render_template, request, redirect
import sqlite3 # Missing tool for database
import requests

app = Flask(__name__)

# YOUR API KEY
API_KEY = "AIzaSyAPNekUGW1nFy1YC5ohKRcKFmblVl15-is"

# This is what pytest is looking for!
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')
    
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

                all_results.append({
                    "title": place.get('name'),
                    "category": item['filter'], 
                    "image": img_url,
                    "desc": place.get('vicinity', 'Nearby service'),
                    "lat": place['geometry']['location']['lat'],
                    "lon": place['geometry']['location']['lng']
                })
    return render_template('index.html', items=all_results)

@app.route('/find_specific')
def find_specific():
    query = request.args.get('name')
    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={lat},{lon}&radius=10000&key={API_KEY}"
    response = requests.get(url).json()
    
    search_results = []
    if "results" in response:
        for place in response["results"]:
            photo_ref = place.get('photos', [{}])[0].get('photo_reference')
            img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}" if photo_ref else "https://via.placeholder.com/400"
            
            search_results.append({
                "title": place.get('name'),
                "category": "search-result",
                "image": img_url,
                "desc": place.get('formatted_address'),
                "lat": place['geometry']['location']['lat'],
                "lon": place['geometry']['location']['lng']
            })
    return render_template('index.html', items=search_results)

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
        conn.execute(
            "INSERT INTO resources (title, category, desc, lat, lon, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (title, category, desc, lat, lon, phone)
        )
        conn.commit()
        conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)