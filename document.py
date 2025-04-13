from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from flask import render_template, request, redirect, url_for, flash

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

        # ✅ Flash hanya jika commit berhasil
        flash("Data project berhasil ditambahkan!", "success")
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

# Route untuk delete user
@app.route('/delete_user/<string:username>', methods=['GET'])
def delete_user(username):
    try:
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        mydb.commit()
        # flash('User berhasil dihapus.', 'success')
    except Exception as e:
        mydb.rollback()
        flash(f'Terjadi kesalahan saat menghapus user: {e}', 'danger')
    return redirect(url_for('dataUsers'))

@app.route('/registerUsers', methods=['GET', 'POST'])
def registerUsers():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        no_pekerja = request.form['no_pekerja']
        nama_pekerja = request.form['nama_pekerja']
        role = request.form['role']

        # Cek apakah no_pekerja sudah ada
        cursor.execute("SELECT * FROM users WHERE no_pekerja = %s", (no_pekerja,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Nomor Pekerja sudah terdaftar. Gunakan nomor lain.', 'danger')
            return redirect(url_for('registerUsers'))

        # Insert user baru
        cursor.execute("""
            INSERT INTO users (username, password, no_pekerja, nama_pekerja, role) 
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password, no_pekerja, nama_pekerja, role))
        mydb.commit()

        flash('User berhasil ditambahkan!', 'success')
        return redirect(url_for('registerUsers'))

    return render_template('registerUsers.html')

@app.route('/edit_user/<username>', methods=['GET', 'POST'])
def edit_user(username):
    if request.method == 'POST':
        new_username = request.form['username']
        password = request.form['password']
        no_pekerja = request.form['no_pekerja']
        nama_pekerja = request.form['nama_pekerja']
        role = request.form['role']

        # Update data di database
        cursor.execute("""
            UPDATE users 
            SET username=%s, password=%s, no_pekerja=%s, nama_pekerja=%s, role=%s 
            WHERE username=%s
        """, (new_username, password, no_pekerja, nama_pekerja, role, username))
        mydb.commit()

        flash('User berhasil diperbarui!', 'success')
        return redirect(url_for('dataUsers'))

    # Ambil data user berdasarkan username
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    return render_template('editUser.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
