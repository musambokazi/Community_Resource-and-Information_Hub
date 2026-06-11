from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, limiter
from app.models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        # Guest shortcut
        if 'guest' in request.form:
            session['guest'] = True
            return redirect('/')

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error="Username and password are required.")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.permanent = True
            session['user_id'] = user.id
            session.pop('guest', None)
            return redirect('/')

        return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')


@auth.route('/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        return render_template('login.html', error="Username and password are required.")

    if len(password) < 8:
        return render_template('login.html', error="Password must be at least 8 characters.")

    existing = User.query.filter_by(username=username).first()
    if existing:
        return render_template('login.html', error="That username is already taken.")

    hashed_pwd = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pwd)
    db.session.add(new_user)
    db.session.commit()

    session.permanent = True
    session['user_id'] = new_user.id
    session.pop('guest', None)
    return redirect('/')


@auth.route('/guest')
@limiter.limit("20 per minute")
def guest():
    session['guest'] = True
    session.pop('user_id', None)
    return redirect('/')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
