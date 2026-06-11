from datetime import datetime
from flask import Blueprint, render_template, redirect, session, make_response, current_app
from app.extensions import limiter
from app.models import User

pages = Blueprint('pages', __name__)


def _get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


@pages.route('/')
@limiter.limit("60 per minute")
def home():
    user = _get_current_user()
    if not user and not session.get('guest'):
        return redirect('/login')
    return render_template('index.html', user=user)


@pages.route('/terms')
def terms():
    return render_template('terms.html')


@pages.route('/privacy')
def privacy():
    return render_template('privacy.html')


@pages.route('/sitemap.xml')
def sitemap():
    base = current_app.config.get('BASE_URL', 'https://yourdomain.com')
    today = datetime.utcnow().strftime('%Y-%m-%d')

    pages_list = [
        {"url": "/",        "priority": 1.0, "changefreq": "daily"},
        {"url": "/terms",   "priority": 0.3, "changefreq": "monthly"},
        {"url": "/privacy", "priority": 0.3, "changefreq": "monthly"},
    ]

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in pages_list:
        lines += [
            "  <url>",
            f"    <loc>{base}{page['url']}</loc>",
            f"    <lastmod>{today}</lastmod>",
            f"    <changefreq>{page['changefreq']}</changefreq>",
            f"    <priority>{page['priority']}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")

    response = make_response("\n".join(lines))
    response.headers["Content-Type"] = "application/xml"
    return response
