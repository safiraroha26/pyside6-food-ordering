import sqlite3

# ======================
# KONEKSI
# ======================
def koneksi():
    return sqlite3.connect("data.db")


# ======================
# SETUP DATABASE
# ======================
def setup_database():
    conn = koneksi()
    cursor = conn.cursor()

    # users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role     TEXT
    )
    """)

    # menu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        nama  TEXT,
        harga INTEGER
    )
    """)

    # pesanan — dengan kolom catatan, status, dan waktu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pesanan (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_user TEXT,
        menu      TEXT,
        jumlah    INTEGER,
        total     INTEGER,
        catatan   TEXT DEFAULT '',
        status    TEXT DEFAULT 'Menunggu',
        waktu     TEXT DEFAULT (datetime('now','localtime'))
    )
    """)

    # === MIGRASI: tambah kolom jika DB lama belum punya ===
    _migrasi_kolom(cursor, "pesanan", "catatan", "TEXT DEFAULT ''")
    _migrasi_kolom(cursor, "pesanan", "status",  "TEXT DEFAULT 'Menunggu'")
    _migrasi_kolom(cursor, "pesanan", "waktu",   "TEXT")

    # default admin
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?)",
            ("admin", "admin123", "admin")
        )

    # default user
    cursor.execute("SELECT * FROM users WHERE username='user'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?)",
            ("user", "user", "user")
        )

    conn.commit()
    conn.close()


def _migrasi_kolom(cursor, tabel, kolom, tipe):
    """Tambah kolom ke tabel jika belum ada (untuk DB lama)."""
    cursor.execute(f"PRAGMA table_info({tabel})")
    kolom_ada = [row[1] for row in cursor.fetchall()]
    if kolom not in kolom_ada:
        cursor.execute(f"ALTER TABLE {tabel} ADD COLUMN {kolom} {tipe}")


# ======================
# CRUD MENU
# ======================
def insert_menu(nama, harga):
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu (nama, harga) VALUES (?, ?)",
        (nama, harga)
    )
    conn.commit()
    conn.close()


def ambil_menu():
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    data = cursor.fetchall()
    conn.close()
    return data


def update_menu(id_menu, nama, harga):
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE menu SET nama=?, harga=? WHERE id=?",
        (nama, harga, id_menu)
    )
    conn.commit()
    conn.close()


def hapus_menu(id_menu):
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id=?", (id_menu,))
    conn.commit()
    conn.close()


# ======================
# PESANAN
# ======================
def insert_pesanan(nama_user, menu, jumlah, total, catatan=""):
    """Simpan pesanan baru dengan status awal 'Menunggu' dan waktu sekarang."""
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO pesanan (nama_user, menu, jumlah, total, catatan, status, waktu)
           VALUES (?, ?, ?, ?, ?, 'Menunggu', datetime('now','localtime'))""",
        (nama_user, menu, jumlah, total, catatan)
    )
    conn.commit()
    conn.close()


def ambil_pesanan():
    """Ambil semua pesanan untuk admin — urut Menunggu dulu."""
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nama_user, menu, jumlah, total, catatan, status, waktu
        FROM pesanan
        ORDER BY
            CASE status
                WHEN 'Menunggu'   THEN 1
                WHEN 'Selesai'    THEN 2
                WHEN 'Dibatalkan' THEN 3
                ELSE 4
            END,
            id ASC
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def ambil_pesanan_user(nama_user):
    """Ambil pesanan milik user tertentu, terbaru di atas."""
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, menu, jumlah, total, catatan, waktu, status
        FROM pesanan
        WHERE nama_user = ?
        ORDER BY id DESC
    """, (nama_user,))
    data = cursor.fetchall()
    conn.close()
    return data


def update_status_pesanan(id_pesanan, status):
    """Update status pesanan: 'Selesai' atau 'Dibatalkan'."""
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pesanan SET status=? WHERE id=?",
        (status, id_pesanan)
    )
    conn.commit()
    conn.close()


# ======================
# USERS / REGISTRASI
# ======================
def cek_username(username):
    """Kembalikan True jika username sudah terdaftar."""
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    ada = cursor.fetchone() is not None
    conn.close()
    return ada


def register_user(username, password):
    """Daftarkan akun baru dengan role 'user'. Return True jika berhasil."""
    if cek_username(username):
        return False
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users VALUES (NULL, ?, ?, 'user')",
        (username, password)
    )
    conn.commit()
    conn.close()
    return True