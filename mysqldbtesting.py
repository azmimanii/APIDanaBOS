from flask import Flask, request, jsonify, flash
from flask_mysqldb import MySQL
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config['MySQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'danabos'

mysql = MySQL(app)

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM kondisiruangan')
    fetchdata = cur.fetchall()
    cur.close()

    # return render_template('index.html', data = fetchdata)
    return jsonify(fetchdata)

@app.route('/insert', methods=['POST'])
def insert():

    if request.method == 'POST':
        ID = request.form['ID']
        nama_kecamatan = request.form['nama_kecamatan']
        nama_sekolah = request.form['nama_sekolah']
        baik = request.form['baik']
        rusak_ringan = request.form['rusak_ringan']
        rusak_sedang = request.form['rusak_sedang']
        rusak_berat = request.form['rusak_berat']
        jumlah_ruangan = request.form['jumlah_ruangan']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO kondisiruangan (ID, nama_kecamatan, nama_sekolah, baik, rusak_ringan, rusak_sedang, rusak_berat, jumlah_ruangan) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ID, nama_kecamatan, nama_sekolah, baik, rusak_ringan, rusak_sedang, rusak_berat, jumlah_ruangan))
        mysql.connection.commit()
        return flash("Data berhasil ditambahkan")

@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        ID = request.form['ID']
        nama_kecamatan = request.form['nama_kecamatan']
        nama_sekolah = request.form['nama_sekolah']
        baik = request.form['baik']
        rusak_ringan = request.form['rusak_ringan']
        rusak_sedang = request.form['rusak_sedang']
        rusak_berat = request.form['rusak_berat']
        jumlah_ruangan = request.form['jumlah_ruangan']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE students
               SET ID=%s, nama_kecamatan=%s, nama_sekolah=%s, baik=%s, rusak_ringan=%s, rusak_sedang=%s, rusak_berat=%s, jumlah_ruangan=%s
               WHERE id=%s
            """, (ID, nama_kecamatan, nama_sekolah, baik, rusak_ringan, rusak_sedang, rusak_berat, jumlah_ruangan))
        flash("Data berhasil diupdate!")
        mysql.connection.commit()
        return redirect(url_for('Index'))


@app.route('/delete/<string:ID>', methods = ['POST', 'GET'])
def delete(ID):
    cur = mysql.connection.cursor()
    print("yeay bisa")
    cur.execute("DELETE FROM kondisiruangan WHERE id=%s", (ID))
    mysql.connection.commit()
    flash("Record berhasil dihapus!")
    return redirect(url_for('Index'))

if __name__ == "__main__":
    app.run(debug = True)