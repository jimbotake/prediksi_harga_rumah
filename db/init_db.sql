CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE rumah (
    id SERIAL PRIMARY KEY,
    luas_bangunan INTEGER,
    jumlah_kamar INTEGER,
    usia_bangunan INTEGER,
    harga INTEGER,
    user_id INTEGER REFERENCES users(id)
);
