import sys
import os

# Ensure backend/ is importable when pytest runs from the project root
_BACKEND = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(_BACKEND))

import pytest
import requests_mock as rm_module
from app import create_app
from app.extensions import db
from app.models import User, CachedResult
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    # Disable talisman redirects in tests
    SERVER_NAME = None


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
    """Verify that SQLAlchemy tables were created."""
    assert 'users' in db.metadata.tables
    assert 'cached_results' in db.metadata.tables


def test_home_redirects_to_login(client):
    """Homepage must redirect unauthenticated/non-guest users to /login."""
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'


def test_health_endpoint(client):
    """Health check must return 200 OK."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


def test_api_nearby_with_mock(client):
    """Nearby API returns mapped place data from mocked Google response."""
    with client.session_transaction() as sess:
        sess['guest'] = True

    with rm_module.Mocker() as m:
        m.get(rm_module.ANY, json={
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


def test_api_search_requires_query(client):
    """Search API returns 400 when q param is missing."""
    with client.session_transaction() as sess:
        sess['guest'] = True
    response = client.get('/api/search')
    assert response.status_code == 400


def test_caching_logic(client, app):
    """Pre-populated cache is returned without hitting external APIs."""
    with app.app_context():
        import json
        from datetime import datetime
        cache = CachedResult(
            lat=-26.2500,
            lon=28.4333,
            results_json=json.dumps([{
                "title": "Cached Clinic",
                "category": "hospital",
                "image": None,
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

    response = client.get('/api/nearby?lat=-26.2500&lon=28.4333')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['cached'] is True
    assert data['data'][0]['title'] == "Cached Clinic"


def test_login_page_renders(client):
    """Login page returns 200."""
    response = client.get('/login')
    assert response.status_code == 200


def test_signup_validates_password_length(client):
    """Signup rejects passwords shorter than 8 chars."""
    response = client.post('/signup', data={
        'username': 'testuser',
        'password': 'short'
    })
    # Should re-render login with error, not redirect
    assert response.status_code == 200


def test_sitemap_xml(client):
    """Sitemap returns valid XML content type."""
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert 'application/xml' in response.content_type
    assert b'<urlset' in response.data


def test_signup_success(client):
    """Signup works with valid credentials (and no DB constraint violations on User)."""
    response = client.post('/signup', data={
        'username': 'newuser123',
        'password': 'validpassword123'
    })
    # Should redirect to home page
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_bookmarks_flow(client):
    """Test creating, fetching, and deleting bookmarks via API."""
    # 1. Get empty bookmarks list
    response = client.get('/api/bookmarks?token=test-token-456')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data'] == []

    # 2. Add a bookmark
    bookmark_data = {
        'token': 'test-token-456',
        'place_id': 'mock-place-789',
        'resource': {
            'title': 'Mock Clinic',
            'category': 'hospital',
            'desc': 'A mock clinic description',
            'lat': -26.2500,
            'lon': 28.4333,
            'is_open': True,
            'place_id': 'mock-place-789'
        }
    }
    response = client.post('/api/bookmarks', json=bookmark_data)
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    assert response.get_json()['bookmarked'] is True

    # 3. Get bookmarks list (should contain 1 bookmark)
    response = client.get('/api/bookmarks?token=test-token-456')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) == 1
    assert data['data'][0]['title'] == 'Mock Clinic'

    # 4. Remove a bookmark (toggle off)
    response = client.post('/api/bookmarks', json={
        'token': 'test-token-456',
        'place_id': 'mock-place-789'
    })
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    assert response.get_json()['bookmarked'] is False

    # 5. Get bookmarks list (should be empty again)
    response = client.get('/api/bookmarks?token=test-token-456')
    assert response.status_code == 200
    assert response.get_json()['data'] == []