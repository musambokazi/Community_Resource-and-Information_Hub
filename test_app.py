import pytest
import requests_mock
from app import create_app
from app.extensions import db
from app.models import User, CachedResult
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_database_integrity(app):
    # Verify that the SQLAlchemy tables exist
    assert 'users' in db.metadata.tables
    assert 'cached_results' in db.metadata.tables

def test_home_redirects_to_login(client):
    # Homepage should redirect to /login if not logged in and not guest
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_api_nearby_with_mock(client):
    # Set guest session to bypass auth if needed
    with client.session_transaction() as sess:
        sess['guest'] = True

    with requests_mock.Mocker() as m:
        # Mock Google Places nearbysearch endpoint
        fake_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        m.get(requests_mock.ANY, json={
            "results": [{
                "name": "Mock Hospital",
                "vicinity": "123 Fake Street",
                "geometry": {"location": {"lat": -26.2500, "lng": 28.4333}},
                "photos": [{"photo_reference": "abc"}]
            }],
            "status": "OK"
        })

        response = client.get('/api/nearby?lat=-26.2500&lon=28.4333')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) > 0
        assert data['data'][0]['title'] == "Mock Hospital"
        assert data['data'][0]['desc'] == "123 Fake Street"

def test_caching_logic(client, app):
    # Pre-populate cache for nearby API
    with app.app_context():
        import json
        from datetime import datetime
        cache = CachedResult(
            lat=-26.2500,
            lon=28.4333,
            results_json=json.dumps([{
                "title": "Cached Clinic",
                "category": "hospital",
                "image": "https://via.placeholder.com/400",
                "desc": "Cached Description",
                "lat": -26.2500,
                "lon": 28.4333,
                "is_open": True,
                "place_id": "cached_123"
            }]),
            timestamp=datetime.utcnow()
        )
        db.session.add(cache)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['guest'] = True

    # Call api_nearby; should return cached result without hitting external APIs
    response = client.get('/api/nearby?lat=-26.2500&lon=28.4333')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['data'][0]['title'] == "Cached Clinic"