import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import psycopg2

# Koneksi ke database
conn = psycopg2.connect(
    host="localhost",
    database="prediksi_db",
    user="postgres",
    password="Humaira31814"
)

# Ambil data dari DB
query = "SELECT luas_bangunan, jumlah_kamar, usia_bangunan, harga FROM rumah"
df = pd.read_sql(query, conn)

# Model
X = df[['luas_bangunan', 'jumlah_kamar', 'usia_bangunan']]
y = df['harga']
model = LinearRegression()
model.fit(X, y)

# Simpan model
joblib.dump(model, 'model.pkl')
print("Model disimpan ke model.pkl")

conn.close()
