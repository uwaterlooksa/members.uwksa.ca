import base64
import datetime
import io
import sqlite3
from functools import wraps

import jwt
import qrcode
from authlib.integrations.flask_client import OAuth
from flask import (Flask, abort, g, jsonify, redirect, render_template,
                   request, session, url_for)

app = Flask(__name__)
app.config.from_object('config')

oauth = OAuth(app)
oauth.register(
    name='oidc',
    client_id=app.config['OIDC_CLIENT_ID'],
    client_secret=app.config['OIDC_CLIENT_SECRET'],
    server_metadata_url=app.config['OIDC_DISCOVERY_URL'],
    client_kwargs={
        'scope': 'openid profile',
    }
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def generate_token(username):
    expiration = datetime.datetime.now(
        tz=datetime.timezone.utc) + datetime.timedelta(seconds=30)
    payload = {
        'username': username,
        'exp': expiration
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


def create_qr_code(token):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data("https://members.uwksa.ca/verify?token=" + token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_byte_array = io.BytesIO()
    img.save(img_byte_array)
    img_byte_array = img_byte_array.getvalue()
    b64 = base64.b64encode(img_byte_array)
    return b64


@app.route('/qr-code')
@login_required
def qr_code_route():
    if request.headers.get('X-Fetch') != 'true':
        abort(403)

    username = session.get('username')
    is_member = session.get('is_member')

    if not username or not is_member:
        return jsonify({'message': 'User not found'}), 404

    token = generate_token(username)
    b64 = create_qr_code(token)
    return b64


@app.route('/verify', methods=['GET'])
def verify():
    if request.args.get('token'):
        token = request.args.get('token')
        try:
            payload = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256'],
                leeway=datetime.timedelta(seconds=10),
            )
        except jwt.ExpiredSignatureError:
            return render_template('verify.html', message='Token expired')
        except jwt.InvalidTokenError:
            return render_template('verify.html', message='Invalid token')
        except Exception as e:
            return render_template('verify.html', message="An error occurred: " + str(e))

        username = payload['username']
        (given_name, family_name, is_member) = get_db().execute(
            'SELECT given_name, family_name, is_member FROM users WHERE username = ? LIMIT 1',
            (username,)
        ).fetchone()

        if not is_member:
            return render_template('verify.html', message='What? How did you get here?')

        return render_template(
            'verify.html',
            message="User verified",
            username=username,
            given_name=given_name,
            family_name=family_name
        )
    else:
        return render_template('verify.html', message='No token to verify')


@app.route('/')
@login_required
def index():
    username = session.get('username')
    is_member = session.get('is_member')

    if not is_member:
        is_member = check_if_member(username)
        session['is_member'] = is_member
        if not is_member:
            return redirect('/join')

    return render_template('base.html', username=username)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True, _scheme='https')
    return oauth.oidc.authorize_redirect(redirect_uri)


def insert_user_into_db(username):
    db = get_db()
    db.execute(
        'INSERT OR IGNORE INTO users (username, given_name, family_name) VALUES (?, ?, ?)',
        (username, session['given_name'], session['family_name'])
    )
    db.commit()


def check_if_member(username):
    db = get_db()
    result = db.execute(
        'SELECT is_member FROM users WHERE username = ? LIMIT 1',
        (username,)
    ).fetchone()
    if result:
        return result['is_member']
    return False


@app.route('/authorize')
def auth():
    token = oauth.oidc.authorize_access_token()

    username = token['userinfo']['username']

    session.permanent = True

    session['username'] = username
    session['given_name'] = token['userinfo']['given_name']
    session['family_name'] = token['userinfo']['family_name']

    insert_user_into_db(username)

    session['is_member'] = check_if_member(username)

    return redirect('/')


@app.route('/join')
def join():
    return jsonify({'message': 'Redirect to WUSA shop page'})
