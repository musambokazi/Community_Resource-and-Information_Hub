from flask import Flask, render_template, request, redirect # Standard Flask tools
import sqlite3 # Database tool
import requests

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db') # Connects to our database file
    conn.row_factory = sqlite3.Row # Lets us access columns by name
    return conn

@app.route('/')
def home():
    lat = request.args.get('lat', '-26.2500') 
    lon = request.args.get('lon', '28.4333')
    
    # We define the categories and their matching images
    categories = [
        {"cat": "police", "img": "https://images.unsplash.com/photo-1596753101905-54318c64dca3?auto=format&fit=crop&w=400"},
        {"cat": "hospital", "img": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=400"},
        {"cat": "library", "img": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=400"},
        {"cat": "taxi_stand", "img": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=400"}
    ]
    
    live_items = []
    for item in categories:
        name = "Local Taxi Rank" if item['cat'] == 'taxi_stand' else f"Nearest {item['cat'].title()}"
        live_items.append({
            "title": name,
            "category": item['cat'],
            "image": item['img'], # This holds the picture URL
            "desc": "Found near your current location.",
            "lat": lat, "lon": lon, "phone": "0115550000"
        })
    
    return render_template('index.html', items=live_items)
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