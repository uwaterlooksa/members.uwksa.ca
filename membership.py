import base64
import datetime
import io
import os
import sqlite3

import jwt
import qrcode
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request


conn = sqlite3.connect('database.db')
cur = conn.cursor()

app = Flask(__name__)
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')


def generate_token(user_id):
    expiration = datetime.datetime.now(
        tz=datetime.timezone.utc) + datetime.timedelta(seconds=30)
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
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
                SECRET_KEY,
                algorithms=['HS256'],
                leeway=datetime.timedelta(seconds=10),
            )
        except jwt.ExpiredSignatureError:
            return render_template('verify.html', message='Token expired')
        except jwt.InvalidTokenError:
            return render_template('verify.html', message='Invalid token')

        user_id = payload['user_id']
        cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        return render_template('verify.html', message="User verified", user=user)
    else:
        return render_template('verify.html', message='No token to verify')


@app.route('/')
def index():
    return render_template('base.html')
