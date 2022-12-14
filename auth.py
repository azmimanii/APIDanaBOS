from flask import Flask, jsonify, request, Blueprint, current_app
import jwt 
import mariadb
import sys
from datetime import datetime, timedelta


auth = Blueprint('auth', __name__)

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
            token = jwt.encode({
                "user_id" : json_data["id"], 
                'exp': datetime.utcnow() + timedelta(minutes=60)
                }, current_app.config['SECRET_KEY'])
            return jsonify({
                'message' : 'Save this token to access API',
                'token' : token
            }), 201
        
        else:
            return "Invalid Username/Password", 401
    
    return "Username Not Found", 404


def checkUserAvailable(cur, body):
    cur.execute(
        f"SELECT * FROM user WHERE username='{body['username']}' AND password='{body['password']}'"
    )
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    for result in rows:
        json_data=(dict(zip(row_headers,result)))
    
    



if __name__ == '__main__':
    auth.run(debug=True)