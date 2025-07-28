from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import joblib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret_key_anda'  # Ganti dengan secret key aman kamu

model = joblib.load('model.pkl')

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="prediksi_db",
        user="postgres",
        password="yourpassword"
    )

# Decorator untuk proteksi route agar harus login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Harus login dulu', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        # Cek apakah username sudah ada
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        existing = cursor.fetchone()
        if existing:
            flash('Username sudah digunakan', 'danger')
            conn.close()
            return redirect(url_for('register'))

        # Insert user baru
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()

        flash('Registrasi berhasil, silakan login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))  # arahkan ke dashboard
        else:
            flash('Username atau password salah', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('Berhasil logout', 'info')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    prediksi = None
    if request.method == 'POST':
        luas = int(request.form['luas'])
        kamar = int(request.form['kamar'])
        usia = int(request.form['usia'])

        input_data = [[luas, kamar, usia]]
        prediksi = round(model.predict(input_data)[0])
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO rumah (luas_bangunan, jumlah_kamar, usia_bangunan, harga, user_id) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (luas, kamar, usia, int(prediksi), session['user_id']))
        conn.commit()
        conn.close()

    return render_template('index.html', prediksi=prediksi)

@app.route('/history')
@login_required
def history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rumah WHERE user_id = %s ORDER BY id DESC", (session['user_id'],))
    data = cursor.fetchall()
    conn.close()
    return render_template('history.html', data=data)

# Kamu bisa tambahkan edit/delete juga dengan @login_required dan cek user_id jika mau

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_connection()
    cursor = conn.cursor()

    # Ambil username
    cursor.execute("SELECT username FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    # Ambil statistik
    cursor.execute("""
        SELECT 
            COUNT(*), 
            AVG(harga), 
            AVG(luas_bangunan),
            AVG(usia_bangunan)
        FROM rumah
        WHERE user_id = %s
    """, (session['user_id'],))
    stats = cursor.fetchone()

    # Ambil data untuk chart
    cursor.execute("""
        SELECT id, harga, luas_bangunan, jumlah_kamar, usia_bangunan 
        FROM rumah 
        WHERE user_id = %s ORDER BY id ASC
    """, (session['user_id'],))
    chart_data = cursor.fetchall()
    conn.close()

    return render_template(
        'dashboard.html',
        username=user[0],
        stats={
            'total': stats[0] or 0,
            'avg_price': round(stats[1] or 0),
            'avg_luas': round(stats[2] or 0),
            'avg_usia': round(stats[3] or 0)
        },
        chart_data=chart_data
    )


if __name__ == '__main__':
    app.run(debug=True)
