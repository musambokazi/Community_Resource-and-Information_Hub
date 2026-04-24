import pytest
import requests_mock
from app import app, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_database_integrity():
    # Real test: checks if your actual SQLite DB is reachable
    conn = get_db_connection()
    assert conn is not None
    # Verify the 'resources' table created in init_db exists
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resources';")
    assert cur.fetchone() is not None
    conn.close()

def test_home_route_with_api_mock(client):
    # Mock test: intercepts the Google API call
    with requests_mock.Mocker() as m:
        # We tell the test to pretend Google sent back one hospital
        fake_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        m.get(requests_mock.ANY, json={
            "results": [{
                "name": "Mock Hospital",
                "vicinity": "123 Fake Street",
                "geometry": {"location": {"lat": -26.2, "lng": 28.4}},
                "photos": [{"photo_reference": "abc"}]
            }],
            "status": "OK"
        })

        # Run the real Flask route logic
        response = client.get('/')
        
        assert response.status_code == 200
        # Check if our 'fake' hospital appears in the real HTML
        assert b"Mock Hospital" in response.data

def test_db_insert_logic(client):
    # We send a "data" dictionary to simulate a form being filled out
    test_data = {
        "title": "Test Clinic",
        "category": "health",
        "desc": "Testing the database insert.",
        "lat": -26.000,
        "lon": 28.000,
        "phone": "0123456789"
    }
    
    # POST the data to the route
    response = client.post('/add', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify it exists in the real database
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM resources WHERE title = ?', ("Test Clinic",)).fetchone()
    assert row is not None
    assert row['phone'] == "0123456789"
    conn.close()