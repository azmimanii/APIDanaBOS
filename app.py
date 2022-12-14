# Module Imports
import mariadb
import sys
from flask import Flask, request
from auth_otp import auth
import json
from functools import wraps
import jwt 
from flask_mail import Mail, Message

# Connect to MariaDB Platform
app = Flask(__name__)
app.config['SECRET_KEY'] = '7eSEw7FDi6FHwBS7WyeVlrSjzWhGT4NW'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '18220030@std.stei.itb.ac.id'
app.config['MAIL_PASSWORD'] = 'zvdomkdzzblvxnir'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.register_blueprint(auth)
mail = Mail(app)

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
    

def token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return json.dumps({'error' : 'Token is missing!'}), 401
        
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = getUserById(cur=cur, id=data['user_id'])
        except Exception as e:
            if(str(e) == 'Signature has expired'):
                return json.dumps({'error' : 'Session has expired. Please log back in!'}), 401
            return json.dumps({'error' : 'Token invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/kr")
@token
def kr(user):
    cur = conn.cursor()
    cur.execute(
    "SELECT * FROM kondisiruangan")
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    json_data=[]
    for result in rows:
        json_data.append(dict(zip(row_headers,result)))
    cur.close()
    return json.dumps({"kondisi ruangan": json_data})


@app.route("/delete-kr", methods=["DELETE"])
@token
def deleteKR(user):
    if request.method == "DELETE":
        cur = conn.cursor()
        id = request.args.get("id")
        cur.execute(
        f"DELETE FROM kondisiruangan WHERE ID = {id}")
        return json.dumps({"message" : "Berhasil menghapus data"})


@app.route("/update-kr", methods=["PUT"])
@token
def updKR(user):
    if request.method == "PUT":
        cur = conn.cursor()
        data = dict(request.json)
        print(data)
        id = data['id']
        nama_kecamatan = data["nama_kecamatan"]
        nama_sekolah = data["nama_sekolah"]
        baik = data["baik"]
        rusak_ringan = data["rusak_ringan"]
        rusak_sedang = data["rusak_sedang"]
        rusak_berat = data["rusak_berat"]
        jumlah_ruangan = data["jumlah_ruangan"]
        cur.execute(
        f'''UPDATE kondisiruangan 
            SET Nama_Kecamatan = '{nama_kecamatan}',
            Nama_Sekolah = '{nama_sekolah}',
            Baik = {baik},
            Rusak_Ringan = {rusak_ringan},
            Rusak_Sedang = {rusak_sedang},
            Rusak_Berat = {rusak_berat},
            Jumlah_Ruangan = {jumlah_ruangan}
            WHERE ID = {id}''')
        return json.dumps({"message" : "Berhasil memperbarui data"})


@app.route("/write-kr", methods=["POST"])
@token
def writeKR(user):
    if request.method == "POST":
        try:
            cur = conn.cursor()
            
            data = dict(request.json)
            id = data['id']
            nama_kecamatan = data["nama_kecamatan"]
            nama_sekolah = data["nama_sekolah"]
            baik = data["baik"]
            rusak_ringan = data["rusak_ringan"]
            rusak_sedang = data["rusak_sedang"]
            rusak_berat = data["rusak_berat"]
            jumlah_ruangan = data["jumlah_ruangan"]
            cur.execute(
            f'''INSERT INTO kondisiruangan (ID, Nama_Kecamatan, Nama_Sekolah, Baik, Rusak_Ringan, Rusak_Sedang, Rusak_Berat, Jumlah_Ruangan)
                VALUE({id}, '{nama_kecamatan}', '{nama_sekolah}', {baik}, {rusak_ringan}, {rusak_sedang}, {rusak_berat}, {jumlah_ruangan});''')
        except Exception as e:
            return json.dumps({"message": str(e)})
        return json.dumps({"message" : "Berhasil menambahkan data"})


def getUserById(cur, id):
    cur.execute(
        f"SELECT * FROM user WHERE id = {id}"
    )
    json_data = None
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    for result in rows:
        json_data=(dict(zip(row_headers,result)))
    return json_data


    
if __name__ == "__main__":
    app.run(debug=True)
    
