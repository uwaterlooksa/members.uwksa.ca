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
        if session.get('user') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def generate_token(user_id):
    expiration = datetime.datetime.now(
        tz=datetime.timezone.utc) + datetime.timedelta(seconds=30)
    payload = {
        'user_id': user_id,
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

    user_id = 1
    token = generate_token(user_id)
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

        user_id = payload['user_id']
        cur = get_db().cursor()
        cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        return render_template('verify.html', message="User verified", user=user)
    else:
        return render_template('verify.html', message='No token to verify')


@app.route('/')
def index():
    user = session.get('user')
    return render_template('base.html', user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True, _scheme='https')
    return oauth.oidc.authorize_redirect(redirect_uri)


@app.route('/authorize')
def auth():
    token = oauth.oidc.authorize_access_token()
    session['user'] = token['userinfo']
    return redirect('/')


@app.route('/join')
def join():
    return jsonify({'message': 'Redirect to WUSA shop page'})
