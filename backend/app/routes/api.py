import json
import requests
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db, limiter
from app.models import CachedResult, Bookmark

api = Blueprint('api', __name__, url_prefix='/api')


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _get_cached(query=None, lat=None, lon=None):
    threshold = datetime.utcnow() - timedelta(hours=24)
    if query:
        res = (
            db.session.query(CachedResult)
            .filter(CachedResult.query == query, CachedResult.timestamp > threshold)
            .first()
        )
    else:
        res = (
            db.session.query(CachedResult)
            .filter(
                db.func.round(db.cast(CachedResult.lat, db.Numeric), 3) == round(float(lat), 3),
                db.func.round(db.cast(CachedResult.lon, db.Numeric), 3) == round(float(lon), 3),
                CachedResult.query == None,
                CachedResult.timestamp > threshold,
            )
            .first()
        )
    return json.loads(res.results_json) if res else None


def _save_cache(results, query=None, lat=None, lon=None):
    cache = CachedResult(
        query=query, lat=lat, lon=lon, results_json=json.dumps(results)
    )
    db.session.add(cache)
    db.session.commit()


def _build_place_dict(place, category, api_key):
    """Normalise a Google Places result into our internal dict."""
    photo_ref = place.get('photos', [{}])[0].get('photo_reference')
    img_url = (
        f"https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth=400&photoreference={photo_ref}&key={api_key}"
        if photo_ref
        else None  # no placeholder.com in prod
    )
    return {
        "title": place.get('name'),
        "category": category,
        "image": img_url,
        "desc": place.get('vicinity') or place.get('formatted_address', 'Nearby service'),
        "lat": place['geometry']['location']['lat'],
        "lon": place['geometry']['location']['lng'],
        "is_open": place.get('opening_hours', {}).get('open_now'),
        "place_id": place.get('place_id'),
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@api.route('/nearby')
@limiter.limit("20 per minute")
def api_nearby():
    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')

    cached = _get_cached(lat=lat, lon=lon)
    if cached:
        return jsonify({"success": True, "data": cached, "cached": True})

    search_types = [
        {'type': 'police',     'filter': 'police'},
        {'type': 'hospital',   'filter': 'hospital'},
        {'type': 'school',     'filter': 'education'},
        {'type': 'taxi_stand', 'filter': 'transport'},
    ]

    api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    all_results = []

    for item in search_types:
        url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lon}&rankby=distance&type={item['type']}&key={api_key}"
        )
        try:
            response = requests.get(url, timeout=5).json()
        except requests.RequestException:
            continue

        for place in response.get("results", [])[:3]:
            all_results.append(_build_place_dict(place, item['filter'], api_key))

    _save_cache(all_results, lat=lat, lon=lon)
    return jsonify({"success": True, "data": all_results, "cached": False})


@api.route('/search')
@limiter.limit("30 per minute")
def api_search():
    query = request.args.get('q', '').strip()
    lat = request.args.get('lat', '-26.2500')
    lon = request.args.get('lon', '28.4333')

    if not query:
        return jsonify({"success": False, "error": "Query parameter 'q' is required."}), 400

    cached = _get_cached(query=query)
    if cached:
        return jsonify({"success": True, "data": cached, "cached": True})

    api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    url = (
        f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={query}&location={lat},{lon}&radius=10000&key={api_key}"
    )

    try:
        response = requests.get(url, timeout=5).json()
    except requests.RequestException:
        return jsonify({"success": False, "error": "Upstream API error."}), 502

    results = [
        _build_place_dict(place, "search-result", api_key)
        for place in response.get("results", [])[:12]
    ]

    _save_cache(results, query=query)
    return jsonify({"success": True, "data": results, "cached": False})


@api.route('/bookmarks', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def api_bookmarks():
    if request.method == 'POST':
        data = request.get_json() or {}
        token = data.get('token')
        place_id = data.get('place_id')
        resource = data.get('resource')

        if not token or not place_id:
            return jsonify({"success": False, "error": "Token and place_id are required."}), 400

        # Check if already bookmarked
        existing = Bookmark.query.filter_by(user_token=token, place_id=place_id).first()
        if existing:
            # Toggle off: delete
            db.session.delete(existing)
            db.session.commit()
            return jsonify({"success": True, "bookmarked": False})
        else:
            # Toggle on: add
            if not resource:
                return jsonify({"success": False, "error": "Resource details required to bookmark."}), 400
            new_bookmark = Bookmark(
                user_token=token,
                place_id=place_id,
                resource_json=json.dumps(resource)
            )
            db.session.add(new_bookmark)
            db.session.commit()
            return jsonify({"success": True, "bookmarked": True})

    else: # GET method
        token = request.args.get('token')
        if not token:
            return jsonify({"success": False, "error": "Token parameter is required."}), 400

        bookmarks = Bookmark.query.filter_by(user_token=token).all()
        data = []
        for b in bookmarks:
            try:
                data.append(json.loads(b.resource_json))
            except Exception:
                continue
        return jsonify({"success": True, "data": data})


@api.route('/health')
def health():
    """Liveness probe for Docker / load balancers."""
    return jsonify({"status": "ok"}), 200
