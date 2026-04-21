from flask import Flask, render_template, request, redirect # Standard Flask tools
import sqlite3 # Database tool
import requests

app = Flask(__name__)
API_KEY = "AIzaSyAPNekUGW1nFy1YC5ohKRcKFmblVl15-is"
def get_db_connection():
    conn = sqlite3.connect('database.db') # Connects to our database file
    conn.row_factory = sqlite3.Row # Lets us access columns by name
    return conn

@app.route('/')
def home():
    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')
    
    # These are the "types" Google understands
    search_types = [
        {'type': 'police', 'filter': 'police'},
        {'type': 'hospital', 'filter': 'hospital'},
        {'type': 'library', 'filter': 'library'},
        {'type': 'taxi_stand', 'filter': 'transport'} # Mapping taxi to your 'transport' button
    ]
    
    all_results = []
    
    for item in search_types:
        # We ask Google for everything within 5km
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=5000&type={item['type']}&key={API_KEY}"
        response = requests.get(url).json()

        if "results" in response:
            # We loop through EVERY result Google found, not just the first one
            for place in response["results"]:
                photo_ref = place.get('photos', [{}])[0].get('photo_reference')
                
                # Get the real photo or a placeholder if Google doesn't have one
                img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}" if photo_ref else "https://via.placeholder.com/400"

                all_results.append({
                    "title": place.get('name'),
                    "category": item['filter'], # This matches your CSS/JS filters
                    "image": img_url,
                    "desc": place.get('vicinity', 'Nearby service'),
                    "lat": place['geometry']['location']['lat'],
                    "lon": place['geometry']['location']['lng']
                })

    return render_template('index.html', items=all_results)
@app.route('/add', methods=['POST'])
def add_resource():

    conn = get_db_connection()

    # Add multiple resources to test the "locate all" functionality
    resources = [
    {
        "title": "Springs Health Clinic", 
        "category": "health", 
        "image": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=400",
        "desc": "Open 24/7 for emergencies.",
        "lat": -26.2500, "lon": 28.4333, "phone": "0115551234"
    },
    {
        "title": "Local Taxi Rank", 
        "category": "transport", 
        "image": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=400",
        "desc": "Main hub for local commutes.",
        "lat": -26.2520, "lon": 28.4320, "phone": "0117778888"
    }
    ]

    for res in resources:
        conn.execute("INSERT INTO resources (title, category, desc, lat, lon, phone) VALUES (?, ?, ?, ?, ?, ?)", res)
    
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/search')
def search():
    user_lat = request.args.get('lat') # Get lat from the browser
    user_lon = request.args.get('lon') # Get lon from the browser
    
    # This is a 'Mock' example of how you call a live API (like Google Places)
    # In a real app, you would use: requests.get(f"https://maps.googleapis.com/...")
    live_results = [
        {"title": "Nearest Police Station", "category": "emergency", "desc": "Live Location Found", "lat": user_lat, "lon": user_lon},
        {"title": "Nearest Fire Station", "category": "emergency", "desc": "Live Location Found", "lat": user_lat, "lon": user_lon}
    ]
    
    return render_template('index.html', items=live_results)

if __name__ == '__main__':
    app.run(debug=True)