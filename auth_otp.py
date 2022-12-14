from flask import Flask, jsonify, request, Blueprint, current_app
import jwt 
import mariadb
import sys
from datetime import datetime, timedelta
import pyotp
from flask_mail import Message, Mail

auth = Blueprint('auth', __name__)

totp = pyotp.TOTP('JKE5UXZ3Q3IJQVXPQQC4NKNNO2XBFQ7R', interval=300)

try:
    conn = mariadb.connect(
        user="root",
        password="",
        host="localhost",
        port=3308,
        database="danabos"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

if(conn):
    cur = conn.cursor()

@auth.route('/signup', methods=["POST"])
def signup():
    cur = conn.cursor()
    request_body = request.json

    body = {
        "username": request_body['username'],
        "password": request_body['password'],
        "email": request_body['email']
    }

    if checkUserAvailable(cur, body):
        return "Username is unavailable!"
    
    else:
        cur.execute(
            f"INSERT INTO user(username, password, email, verified, admin) VALUES ('{body['username']}', '{body['password']}', '{body['email']}', 0, 0)"
        )
        conn.commit()
        cur.close()
        return "New Account Created Successfully"
    
@auth.route('/login', methods=["POST"])
def login():
    cur = conn.cursor()
    request_body = request.json

    body = {
        "username": request_body['username'],
        "password": request_body['password']
    }

    cur.execute(
        f"SELECT * FROM user WHERE username='{body['username']}'"
    )
    json_data = None
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    
    for result in rows:
        json_data=(dict(zip(row_headers,result)))
    
    if(json_data):
        if (body["password"]==json_data["password"]):
            with current_app.app_context():
                mail = Mail()
                msg = Message(
                'OTP API Dana BOS',
                sender = current_app.config['MAIL_USERNAME'],
                recipients = [json_data['email']]
                )
                user_otp = totp.now()
                msg.body = f'Kode OTP Anda: {user_otp}. OTP Berlaku selama 5 menit. Selamat login ^_^'
                mail.send(msg)
                return jsonify({
                    'message' : 'Please check your email for OTP code.',
                }), 201
        
        else:
            return "Invalid Username/Password", 401
    
    return "Username Not Found", 404

@auth.route('/verify-otp', methods=["GET"])
def verifyOTP():
    cur = conn.cursor()
    request_body = request.json

    body = {
        "username": request_body['username'],
        "otp": request_body['otp']
    }

    cur.execute(
        f"SELECT * FROM user WHERE username='{body['username']}'"
    )
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    
    for result in rows:
        json_data=(dict(zip(row_headers,result)))
    
    if(json_data):
        if (totp.verify(body['otp'])):
            token = jwt.encode({
                "user_id" : json_data["id"], 
                'exp': datetime.utcnow() + timedelta(minutes=60)
                }, current_app.config['SECRET_KEY'])
            return jsonify({
                'message' : 'Save this token to access API',
                'token' : token
            }), 201
        return "Invalid OTP",
    
    else:
        return "Invalid Username/Password", 401

def checkUserAvailable(cur, body):
    json_data = None
    cur.execute(
        f"SELECT * FROM user WHERE username='{body['username']}' AND password='{body['password']}'"
    )
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    for result in rows:
        json_data=(dict(zip(row_headers,result)))
    
    return json_data

# def checkSessionAvailable(cur, body):
#     cur.execute(
#         f"SELECT * FROM session WHERE user_id={body['id']}"
#     )
#     row_headers=[x[0] for x in cur.description]
#     rows = cur.fetchall()
#     for result in rows:
#         json_data=(dict(zip(row_headers,result)))
    
#     return json_data


if __name__ == '__main__':
    auth.run(debug=True)