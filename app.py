from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="skhujpg9h2jx",
    database="document_v1"
)
cursor = mydb.cursor(dictionary=True)

# @app.route('/')
# def index():
#     cursor.execute("SELECT username, password, no_pekerja, nama_pekerja, role FROM users")
#     users = cursor.fetchall()
#     return render_template('index.html', users=users)

@app.route('/')
def index():
    if 'user' not in session or session['role'].lower() != 'admin':
        return redirect(url_for('login'))
    cursor.execute("SELECT username, password, no_pekerja, nama_pekerja, role FROM users")
    users = cursor.fetchall()
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            if user['role'].lower() == 'admin':  # Convert role to lowercase for case-insensitive check
                session['user'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('index'))
            else:
                flash("Username or password is incorrect, please try again.", "danger")
                return redirect(url_for('login'))
        else:
            flash("Username or password is incorrect, please try again.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        no_pekerja = request.form['no_pekerja']
        nama_pekerja = request.form['nama_pekerja']
        role = request.form['role']

        # Check if no_pekerja already exists
        cursor.execute("SELECT * FROM users WHERE no_pekerja = %s", (no_pekerja,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('No Pekerja already exists! Please use a different No Pekerja.', 'danger')
            return redirect(url_for('register'))

        # Insert new user if no_pekerja is unique
        cursor.execute("""
            INSERT INTO users (username, password, no_pekerja, nama_pekerja, role) 
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password, no_pekerja, nama_pekerja, role))
        mydb.commit()

        flash('User registered successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')
    
@app.route('/edit/<username>', methods=['GET', 'POST'])
def edit_user(username):
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_username = request.form['username']
        password = request.form['password']
        no_pekerja = request.form['no_pekerja']
        nama_pekerja = request.form['nama_pekerja']
        role = request.form['role']

        # Check if the new no_pekerja already exists for another user
        cursor.execute("SELECT * FROM users WHERE no_pekerja = %s AND username != %s", (no_pekerja, username))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('No Pekerja already exists! Please use a different No Pekerja.', 'danger')
            return redirect(url_for('edit_user', username=username))

        # Update the user data
        cursor.execute("""
            UPDATE users 
            SET username=%s, password=%s, no_pekerja=%s, nama_pekerja=%s, role=%s 
            WHERE username=%s
        """, (new_username, password, no_pekerja, nama_pekerja, role, username))
        mydb.commit()

        flash('User updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', user=user)

@app.route('/delete/<username>', methods=['GET'])
def delete_user(username):
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    mydb.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)