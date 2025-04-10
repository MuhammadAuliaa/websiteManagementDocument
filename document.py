from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Koneksi ke database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="skhujpg9h2jx",
    database="document_v1"
)
cursor = mydb.cursor(dictionary=True)

@app.route('/')
def home():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM project_event")
    data = cursor.fetchall()
    cursor.close()
    return render_template('main.html', project_data=data)

# Route halaman form input
@app.route('/inputEvents', methods=['GET'])
def inputEvents():
    return render_template('inputEvents.html')

# Route untuk submit data project
@app.route('/submit-project', methods=['POST'])
def submit_project():
    try:
        kode_project = request.form['kode_project']
        judul_project = request.form['judul_project']
        tanggal_event = request.form['tanggal_event']
        hari_kerja = request.form['hari_kerja']
        nama_venue = request.form['nama_venue']
        jenis_pekerjaan = request.form['jenis_pekerjaan']
        keterangan = request.form['keterangan']
        approval_status = request.form['approval_status']

        cursor = mydb.cursor()
        query = """
            INSERT INTO project_event (
                kode_project, judul_project, tanggal_event, hari_kerja,
                nama_venue, jenis_pekerjaan, keterangan, approval_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            kode_project, judul_project, tanggal_event, hari_kerja,
            nama_venue, jenis_pekerjaan, keterangan, approval_status
        )

        cursor.execute(query, values)
        mydb.commit()
        cursor.close()

        flash("Data project berhasil disimpan!", "success")
        return redirect(url_for('inputEvents'))

    except Exception as e:
        flash(f"Terjadi kesalahan: {str(e)}", "danger")
        return redirect(url_for('inputEvents'))
    
# Route halaman form input
@app.route('/dataUsers', methods=['GET'])
def dataUsers():
    cursor.execute("SELECT * FROM users")
    users_data = cursor.fetchall()
    return render_template('dataUser.html', users=users_data)

if __name__ == '__main__':
    app.run(debug=True)
