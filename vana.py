from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "mysecretkey"

# 🔧 ฟังก์ชันเชื่อมฐานข้อมูล
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🧱 สร้างตารางถ้ายังไม่มี
def init_db():
    if not os.path.exists('database.db'):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        ''')
        conn.execute('''
            CREATE TABLE contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                body TEXT
            );
        ''')
        # เพิ่มแอดมินเริ่มต้น
        conn.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()
        conn.close()

init_db()

# 🏠 หน้าแรก แสดงเนื้อหา
@app.route('/')
def index():
    conn = get_db_connection()
    contents = conn.execute('SELECT * FROM contents').fetchall()
    conn.close()
    return render_template('index.html', contents=contents)

# 🔐 หน้า login สำหรับ admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE username=? AND password=?',
                             (username, password)).fetchone()
        conn.close()
        if admin:
            session['admin'] = username
            return redirect('/admin')
        else:
            return "❌ Invalid username or password!"
    return render_template('login.html')

# 👑 หน้า admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin' not in session:
        return redirect('/login')
    
    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        conn.execute('INSERT INTO contents (title, body) VALUES (?, ?)', (title, body))
        conn.commit()

    contents = conn.execute('SELECT * FROM contents').fetchall()
    conn.close()
    return render_template('admin.html', contents=contents, admin=session['admin'])

# 🚪 logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
