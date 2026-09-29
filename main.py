import os
import sys
import sqlite3
import database

from PySide6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QLabel,
    QAbstractItemView, QMessageBox
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer, Qt


def resource_path(relative_path):
    """Ambil path yang benar saat development maupun saat jadi .exe"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def load_ui(nama_file):
    """Load file .ui dengan path yang benar, cocok untuk .exe maupun development"""
    path = resource_path(os.path.join("ui", nama_file))
    file = QFile(path)
    file.open(QFile.ReadOnly)
    loader = QUiLoader()
    window = loader.load(file)
    file.close()
    return window


# ======================
# TOAST MODERN
# ======================
class Toast(QLabel):
    def __init__(self, parent, message, color="#2ecc71"):
        super().__init__(parent)

        self.setText(message)
        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 12px;
            }}
        """)

        self.adjustSize()

        x = parent.width() - self.width() - 20
        y = parent.height() - self.height() - 20
        self.move(x, y)

        self.show()

        QTimer.singleShot(2000, self.close)


# ======================
# CUSTOM CONFIRM DIALOG
# ======================
class KonfirmasiDialog:
    """
    Pengganti QMessageBox.question() dengan tampilan yang bisa di-styling penuh.
    Penggunaan:
        hasil = KonfirmasiDialog.tanya(parent, "Judul", "Pesan kamu?")
        if hasil:  # True = Yes, False = No
            ...
    """

    STYLE = """
        QDialog {
            background-color: #f4f6f8;
            font-family: "Segoe UI";
        }
        QLabel#labelPesan {
            color: #2c3e50;
            font-size: 13px;
            padding: 10px 0px;
        }
        QLabel#labelJudul {
            color: #1a252f;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton {
            font-family: "Segoe UI";
            font-size: 12px;
            font-weight: bold;
            color: white;
            border-radius: 6px;
            padding: 7px 24px;
            min-width: 80px;
            min-height: 30px;
            border: none;
        }
        QPushButton#btnYes {
            background-color: #27ae60;
        }
        QPushButton#btnYes:hover {
            background-color: #1e8449;
        }
        QPushButton#btnYes:pressed {
            background-color: #196f3d;
        }
        QPushButton#btnNo {
            background-color: #e74c3c;
        }
        QPushButton#btnNo:hover {
            background-color: #c0392b;
        }
        QPushButton#btnNo:pressed {
            background-color: #a93226;
        }
    """

    @staticmethod
    def tanya(parent, judul, pesan):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PySide6.QtCore import Qt

        dialog = QDialog(parent)
        dialog.setWindowTitle(judul)
        dialog.setStyleSheet(KonfirmasiDialog.STYLE)
        dialog.setMinimumWidth(320)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        # Judul
        lbl_judul = QLabel(judul)
        lbl_judul.setObjectName("labelJudul")
        layout.addWidget(lbl_judul)

        # Pesan
        lbl_pesan = QLabel(pesan)
        lbl_pesan.setObjectName("labelPesan")
        lbl_pesan.setWordWrap(True)
        layout.addWidget(lbl_pesan)

        # Tombol
        layout_btn = QHBoxLayout()
        layout_btn.setSpacing(10)
        layout_btn.addStretch()

        btn_yes = QPushButton("Ya")
        btn_yes.setObjectName("btnYes")
        btn_no  = QPushButton("Tidak")
        btn_no.setObjectName("btnNo")

        layout_btn.addWidget(btn_yes)
        layout_btn.addWidget(btn_no)
        layout.addLayout(layout_btn)

        hasil = [False]

        def on_yes():
            hasil[0] = True
            dialog.accept()

        def on_no():
            hasil[0] = False
            dialog.reject()

        btn_yes.clicked.connect(on_yes)
        btn_no.clicked.connect(on_no)

        dialog.exec()
        return hasil[0]


# ======================
# LOGIN & REGISTRASI
# ======================
class Login(QWidget):
    def __init__(self):
        super().__init__()

        self.window = load_ui("login.ui")

        # Widget login
        self.input_user       = self.window.findChild(QLineEdit,       "input_user")
        self.input_pass       = self.window.findChild(QLineEdit,       "input_pass")
        self.btn_login        = self.window.findChild(QPushButton,     "btn_login")

        # Widget daftar
        self.input_reg_user    = self.window.findChild(QLineEdit,      "input_reg_user")
        self.input_reg_pass    = self.window.findChild(QLineEdit,      "input_reg_pass")
        self.input_reg_konfirm = self.window.findChild(QLineEdit,      "input_reg_konfirm")
        self.btn_daftar        = self.window.findChild(QPushButton,    "btn_daftar")

        # Toggle tab
        self.btn_tab_login  = self.window.findChild(QPushButton, "btnTabLogin")
        self.btn_tab_daftar = self.window.findChild(QPushButton, "btnTabDaftar")
        self.stacked        = self.window.findChild(QWidget,     "stackedWidget")

        self._set_tab_style()

        # Signal login
        self.btn_login.clicked.connect(self.login)
        self.input_user.returnPressed.connect(self.login)
        self.input_pass.returnPressed.connect(self.login)

        # Signal daftar
        self.btn_daftar.clicked.connect(self.daftar)
        self.input_reg_konfirm.returnPressed.connect(self.daftar)

        # Signal toggle
        self.btn_tab_login.clicked.connect(lambda: self.ganti_tab(0))
        self.btn_tab_daftar.clicked.connect(lambda: self.ganti_tab(1))

        self.window.show()

    def ganti_tab(self, index):
        self.stacked.setCurrentIndex(index)
        self.btn_tab_login.setChecked(index == 0)
        self.btn_tab_daftar.setChecked(index == 1)
        self._set_tab_style()

    def _set_tab_style(self):
        aktif = """
            background-color: #2c3e50;
            color: white;
            border-radius: 0px;
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
            font-family: 'Segoe UI';
            min-height: 32px;
            border: none;
        """
        nonaktif = """
            background-color: #dcdde1;
            color: #2c3e50;
            border-radius: 0px;
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
            font-family: 'Segoe UI';
            min-height: 32px;
            border: none;
        """
        self.btn_tab_login.setStyleSheet(aktif   if self.btn_tab_login.isChecked()  else nonaktif)
        self.btn_tab_daftar.setStyleSheet(aktif  if self.btn_tab_daftar.isChecked() else nonaktif)

    def login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()

        if not username or not password:
            Toast(self.window, "Username & Password wajib diisi!", "#e74c3c")
            return

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        )
        data = cursor.fetchone()
        conn.close()

        if data:
            role = data[0]
            self.window.close()
            if role == "admin":
                self.next = Admin()
            else:
                self.next = User(username)
        else:
            Toast(self.window, "Username atau Password salah!", "#e74c3c")

    def daftar(self):
        username = self.input_reg_user.text().strip()
        password = self.input_reg_pass.text()
        konfirm  = self.input_reg_konfirm.text()

        if not username or not password or not konfirm:
            Toast(self.window, "Semua field wajib diisi!", "#e74c3c")
            return
        if len(username) < 3:
            Toast(self.window, "Username minimal 3 karakter!", "#e74c3c")
            return
        if len(password) < 4:
            Toast(self.window, "Password minimal 4 karakter!", "#e74c3c")
            return
        if password != konfirm:
            Toast(self.window, "Konfirmasi password tidak cocok!", "#e74c3c")
            return

        if database.register_user(username, password):
            Toast(self.window, f"Akun '{username}' berhasil dibuat!", "#2ecc71")
            self.input_user.setText(username)
            self.input_pass.clear()
            self.input_reg_user.clear()
            self.input_reg_pass.clear()
            self.input_reg_konfirm.clear()
            QTimer.singleShot(1200, lambda: self.ganti_tab(0))
        else:
            Toast(self.window, f"Username '{username}' sudah dipakai!", "#e74c3c")


# ======================
# ADMIN
# ======================
class Admin(QWidget):
    def __init__(self):
        super().__init__()

        self.window = load_ui("admin.ui")

        self.input_nama    = self.window.findChild(QLineEdit,   "input_nama")
        self.input_harga   = self.window.findChild(QLineEdit,   "input_harga")
        self.btn_simpan    = self.window.findChild(QPushButton, "btn_simpan")
        self.btn_update    = self.window.findChild(QPushButton, "btn_update")
        self.btn_hapus     = self.window.findChild(QPushButton, "btn_hapus")
        self.btn_reset     = self.window.findChild(QPushButton, "btnReset")
        self.btn_logout    = self.window.findChild(QPushButton, "btn_logout")
        self.table         = self.window.findChild(QTableWidget, "table_menu")
        self.table_pesanan = self.window.findChild(QTableWidget, "table_pesanan")
        self.btn_selesai   = self.window.findChild(QPushButton, "btnSelesai")
        self.btn_batalkan  = self.window.findChild(QPushButton, "btnBatalkan")

        self.id_terpilih         = None
        self.id_pesanan_terpilih = None

        # Signal form menu
        self.btn_simpan.clicked.connect(self.simpan_data)
        self.btn_update.clicked.connect(self.update_data)
        self.btn_hapus.clicked.connect(self.hapus_data)
        self.btn_reset.clicked.connect(self.reset_form)
        self.btn_logout.clicked.connect(self.logout)
        self.table.cellClicked.connect(self.pilih_data)

        # Signal tabel pesanan
        self.table_pesanan.cellClicked.connect(self.pilih_pesanan)
        self.btn_selesai.clicked.connect(self.tandai_selesai)
        self.btn_batalkan.clicked.connect(self.batalkan_pesanan)

        # Nonaktifkan tombol aksi pesanan dulu
        self.btn_selesai.setEnabled(False)
        self.btn_batalkan.setEnabled(False)

        self.tampilkan_data()
        self.tampilkan_pesanan()

        self.window.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.tampilkan_pesanan)
        self.timer.start(3000)

    def tampilkan_data(self):
        data = database.ambil_menu()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(3)
        for row, item in enumerate(data):
            for col, val in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(str(val)))

    def simpan_data(self):
        nama  = self.input_nama.text()
        harga = self.input_harga.text()

        if nama == "" or harga == "":
            Toast(self.window, "Nama & harga wajib diisi!", "#e74c3c")
            return

        if not harga.isdigit():
            Toast(self.window, "Harga harus angka!", "#e74c3c")
            return

        database.insert_menu(nama, int(harga))
        self.tampilkan_data()
        self.reset_form()
        Toast(self.window, "Menu berhasil ditambahkan!", "#2ecc71")

    def pilih_data(self, row, column):
        self.id_terpilih = int(self.table.item(row, 0).text())
        self.input_nama.setText(self.table.item(row, 1).text())
        self.input_harga.setText(self.table.item(row, 2).text())

    def update_data(self):
        if not self.id_terpilih:
            Toast(self.window, "Pilih data dulu!", "#e74c3c")
            return

        database.update_menu(
            self.id_terpilih,
            self.input_nama.text(),
            int(self.input_harga.text())
        )
        self.tampilkan_data()
        self.reset_form()
        Toast(self.window, "Menu berhasil diupdate!", "#2ecc71")

    def hapus_data(self):
        if not self.id_terpilih:
            Toast(self.window, "Pilih data dulu!", "#e74c3c")
            return

        if KonfirmasiDialog.tanya(self.window, "Konfirmasi", "Yakin ingin menghapus menu ini?"):
            database.hapus_menu(self.id_terpilih)
            self.tampilkan_data()
            self.reset_form()
            Toast(self.window, "Menu berhasil dihapus!", "#2ecc71")

    def reset_form(self):
        self.input_nama.clear()
        self.input_harga.clear()
        self.id_terpilih = None

    def tampilkan_pesanan(self):
        from PySide6.QtGui import QColor

        baris_aktif = self.table_pesanan.currentRow()

        data = database.ambil_pesanan()
        self.table_pesanan.setRowCount(len(data))

        warna_status = {
            "Menunggu"  : QColor("#fff9c4"),
            "Selesai"   : QColor("#c8f7c5"),
            "Dibatalkan": QColor("#fcd6d3"),
        }

        for row, item in enumerate(data):
            # (id, nama_user, menu, jumlah, total, catatan, status, waktu)
            id_p, nama_user, menu, jumlah, total, catatan, status, waktu = item

            values = [
                str(id_p),
                nama_user,
                menu,
                str(jumlah),
                f"Rp {total:,}",
                catatan if catatan else "-",
                status,
            ]

            warna = warna_status.get(status, QColor("#ffffff"))

            for col, val in enumerate(values):
                cell = QTableWidgetItem(val)
                cell.setBackground(warna)
                self.table_pesanan.setItem(row, col, cell)

        if baris_aktif >= 0:
            self.table_pesanan.selectRow(baris_aktif)

    def pilih_pesanan(self, row, column):
        item = self.table_pesanan.item(row, 0)
        if not item:
            return

        self.id_pesanan_terpilih = int(item.text())
        status = self.table_pesanan.item(row, 6).text()

        # Hanya aktifkan tombol jika pesanan masih Menunggu
        aktif = (status == "Menunggu")
        self.btn_selesai.setEnabled(aktif)
        self.btn_batalkan.setEnabled(aktif)

    def tandai_selesai(self):
        if not self.id_pesanan_terpilih:
            Toast(self.window, "Pilih pesanan dulu!", "#e74c3c")
            return
        database.update_status_pesanan(self.id_pesanan_terpilih, "Selesai")
        self.id_pesanan_terpilih = None
        self.btn_selesai.setEnabled(False)
        self.btn_batalkan.setEnabled(False)
        self.tampilkan_pesanan()
        Toast(self.window, "Pesanan ditandai Selesai!", "#2ecc71")

    def batalkan_pesanan(self):
        if not self.id_pesanan_terpilih:
            Toast(self.window, "Pilih pesanan dulu!", "#e74c3c")
            return
        if KonfirmasiDialog.tanya(self.window, "Batalkan Pesanan", "Yakin ingin membatalkan pesanan ini?"):
            database.update_status_pesanan(self.id_pesanan_terpilih, "Dibatalkan")
            self.id_pesanan_terpilih = None
            self.btn_selesai.setEnabled(False)
            self.btn_batalkan.setEnabled(False)
            self.tampilkan_pesanan()
            Toast(self.window, "Pesanan dibatalkan.", "#e74c3c")

    def logout(self):
        if KonfirmasiDialog.tanya(self.window, "Logout", "Yakin ingin logout?"):
            self.timer.stop()
            self.window.close()
            self.next = Login()


# ======================
# CART (KERANJANG)
# ======================
class Cart(QWidget):
    def __init__(self, username, keranjang, user_ref):
        """
        username  : nama user yang login
        keranjang : list of dict — [{'nama': ..., 'harga': ..., 'jumlah': ..., 'subtotal': ...}, ...]
        user_ref  : referensi ke objek User agar bisa kembali ke halaman user
        """
        super().__init__()

        self.username  = username
        self.keranjang = keranjang
        self.user_ref  = user_ref

        self.window = load_ui("cart.ui")

        # Widget
        self.table_keranjang  = self.window.findChild(QTableWidget, "tableKeranjang")
        self.input_jumlah_item = self.window.findChild(QLineEdit, "inputJumlahItem")
        self.input_total_harga = self.window.findChild(QLineEdit, "inputTotalHarga")
        self.input_catatan     = self.window.findChild(QLineEdit, "inputCatatan")
        self.btn_hapus_item    = self.window.findChild(QPushButton, "btnHapusItem")
        self.btn_kosongkan     = self.window.findChild(QPushButton, "btnKosongkan")
        self.btn_kembali       = self.window.findChild(QPushButton, "btnKembali")
        self.btn_konfirmasi    = self.window.findChild(QPushButton, "btnKonfirmasi")

        # Signal
        self.btn_hapus_item.clicked.connect(self.hapus_item)
        self.btn_kosongkan.clicked.connect(self.kosongkan)
        self.btn_kembali.clicked.connect(self.kembali)
        self.btn_konfirmasi.clicked.connect(self.konfirmasi)

        self.tampilkan_keranjang()
        self.window.show()

    # ── Tampilkan isi keranjang ke tabel ──────────────────────
    def tampilkan_keranjang(self):
        self.table_keranjang.setRowCount(len(self.keranjang))

        for row, item in enumerate(self.keranjang):
            self.table_keranjang.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table_keranjang.setItem(row, 1, QTableWidgetItem(item["nama"]))
            self.table_keranjang.setItem(row, 2, QTableWidgetItem(f"Rp {item['harga']:,}"))
            self.table_keranjang.setItem(row, 3, QTableWidgetItem(str(item["jumlah"])))
            self.table_keranjang.setItem(row, 4, QTableWidgetItem(f"Rp {item['subtotal']:,}"))

        self.update_ringkasan()

    # ── Update total item & total harga ───────────────────────
    def update_ringkasan(self):
        total_item  = sum(i["jumlah"] for i in self.keranjang)
        total_harga = sum(i["subtotal"] for i in self.keranjang)

        self.input_jumlah_item.setText(f"{total_item} item")
        self.input_total_harga.setText(f"Rp {total_harga:,}")

    # ── Hapus 1 baris yang dipilih ────────────────────────────
    def hapus_item(self):
        row = self.table_keranjang.currentRow()

        if row < 0:
            Toast(self.window, "Pilih item dulu!", "#e74c3c")
            return

        nama = self.keranjang[row]["nama"]
        self.keranjang.pop(row)
        self.tampilkan_keranjang()

        # Update tombol keranjang di halaman user
        self.user_ref.update_btn_keranjang()

        Toast(self.window, f"{nama} dihapus dari keranjang.", "#f39c12")

    # ── Kosongkan seluruh keranjang ───────────────────────────
    def kosongkan(self):
        if not self.keranjang:
            Toast(self.window, "Keranjang sudah kosong!", "#f39c12")
            return

        if KonfirmasiDialog.tanya(self.window, "Kosongkan Keranjang", "Yakin ingin mengosongkan semua pesanan?"):
            self.keranjang.clear()
            self.tampilkan_keranjang()
            self.user_ref.update_btn_keranjang()
            Toast(self.window, "Keranjang dikosongkan.", "#f39c12")

    # ── Kembali ke halaman User (keranjang tetap tersimpan) ───
    def kembali(self):
        self.window.close()
        self.user_ref.window.show()

    # ── Konfirmasi → simpan ke DB → bersihkan keranjang ──────
    def konfirmasi(self):
        if not self.keranjang:
            Toast(self.window, "Keranjang masih kosong!", "#e74c3c")
            return

        total_item  = sum(i['jumlah']   for i in self.keranjang)
        total_harga = sum(i['subtotal'] for i in self.keranjang)

        if KonfirmasiDialog.tanya(
            self.window, "Konfirmasi Pesanan",
            f"Pesan {total_item} item?\nTotal: Rp {total_harga:,}"
        ):
            catatan = self.input_catatan.text()

            for item in self.keranjang:
                database.insert_pesanan(
                    self.username,
                    item["nama"],
                    item["jumlah"],
                    item["subtotal"],
                    catatan          # ← catatan dikirim ke DB
                )

            self.keranjang.clear()
            self.user_ref.update_btn_keranjang()

            Toast(self.window, "Pesanan berhasil dikonfirmasi!", "#2ecc71")

            # Kembali ke halaman user setelah 1.5 detik
            QTimer.singleShot(1500, self.kembali)


# ======================
# RIWAYAT PESANAN
# ======================
class Riwayat(QWidget):
    def __init__(self, username, user_ref):
        super().__init__()

        self.username = username
        self.user_ref = user_ref
        self.id_pesanan_terpilih = None

        self.window = load_ui("riwayat.ui")

        self.table      = self.window.findChild(QTableWidget, "tableRiwayat")
        self.label_user = self.window.findChild(QLabel,       "labelUser")
        self.btn_kembali  = self.window.findChild(QPushButton, "btnKembali")
        self.btn_refresh  = self.window.findChild(QPushButton, "btnRefresh")
        self.btn_batalkan = self.window.findChild(QPushButton, "btnBatalkan")

        self.label_user.setText(f"Halo, {username}! Berikut riwayat pesananmu.")
        self.btn_batalkan.setEnabled(False)

        self.table.cellClicked.connect(self.pilih_baris)
        self.btn_kembali.clicked.connect(self.kembali)
        self.btn_refresh.clicked.connect(self.tampilkan)
        self.btn_batalkan.clicked.connect(self.batalkan)

        self.tampilkan()

        # Auto-refresh tiap 5 detik
        self.timer = QTimer()
        self.timer.timeout.connect(self.tampilkan)
        self.timer.start(5000)

        self.window.show()

    def tampilkan(self):
        from PySide6.QtGui import QColor

        baris_aktif = self.table.currentRow()
        data = database.ambil_pesanan_user(self.username)
        self.table.setRowCount(len(data))

        warna_status = {
            "Menunggu"  : QColor("#fff9c4"),
            "Selesai"   : QColor("#c8f7c5"),
            "Dibatalkan": QColor("#fcd6d3"),
        }

        for row, item in enumerate(data):
            # (id, menu, jumlah, total, catatan, waktu, status)
            id_p, menu, jumlah, total, catatan, waktu, status = item
            values = [
                str(id_p), menu, str(jumlah),
                f"Rp {total:,}",
                catatan if catatan else "-",
                waktu if waktu else "-",
                status,
            ]
            warna = warna_status.get(status, QColor("#ffffff"))
            for col, val in enumerate(values):
                cell = QTableWidgetItem(val)
                cell.setBackground(warna)
                self.table.setItem(row, col, cell)

        if baris_aktif >= 0:
            self.table.selectRow(baris_aktif)

    def pilih_baris(self, row, column):
        item = self.table.item(row, 0)
        if not item:
            return
        self.id_pesanan_terpilih = int(item.text())
        status = self.table.item(row, 6).text()
        self.btn_batalkan.setEnabled(status == "Menunggu")

    def batalkan(self):
        if not self.id_pesanan_terpilih:
            Toast(self.window, "Pilih pesanan dulu!", "#e74c3c")
            return
        if KonfirmasiDialog.tanya(
            self.window, "Batalkan Pesanan",
            "Yakin ingin membatalkan pesanan ini?"
        ):
            database.update_status_pesanan(self.id_pesanan_terpilih, "Dibatalkan")
            self.id_pesanan_terpilih = None
            self.btn_batalkan.setEnabled(False)
            self.tampilkan()
            Toast(self.window, "Pesanan berhasil dibatalkan.", "#f39c12")

    def kembali(self):
        self.timer.stop()
        self.window.close()
        self.user_ref.window.show()


# ======================
# USER
# ======================
class User(QWidget):
    def __init__(self, username):
        super().__init__()

        self.username  = username
        self.keranjang = []

        self.window = load_ui("user.ui")

        # Widget
        self.table_menu   = self.window.findChild(QTableWidget, "tableMenu")
        self.input_menu   = self.window.findChild(QLineEdit, "inputNama")
        self.input_harga  = self.window.findChild(QLineEdit, "inputHarga")
        self.spin_jumlah  = self.window.findChild(QSpinBox, "spinJumlah")
        self.input_total  = self.window.findChild(QLineEdit, "inputTotal")
        self.btn_pesan     = self.window.findChild(QPushButton, "btnPesan")
        self.btn_keranjang = self.window.findChild(QPushButton, "btnKeranjang")
        self.btn_riwayat   = self.window.findChild(QPushButton, "btnRiwayat")
        self.btn_logout    = self.window.findChild(QPushButton, "btnLogout")

        self.input_menu.setReadOnly(True)
        self.input_harga.setReadOnly(True)
        self.input_total.setReadOnly(True)

        self.table_menu.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_menu.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_menu.setSelectionMode(QAbstractItemView.SingleSelection)

        # Signal
        self.table_menu.cellClicked.connect(self.pilih_menu)
        self.spin_jumlah.valueChanged.connect(self.hitung_total)
        self.btn_pesan.clicked.connect(self.tambah_ke_keranjang)
        self.btn_keranjang.clicked.connect(self.buka_keranjang)
        self.btn_riwayat.clicked.connect(self.buka_riwayat)
        self.btn_logout.clicked.connect(self.logout)

        self.load_menu()
        self.update_btn_keranjang()
        self.window.show()

    # ── Load menu dari database ────────────────────────────────
    def load_menu(self):
        data = database.ambil_menu()
        self.table_menu.setRowCount(len(data))
        self.table_menu.setColumnCount(3)
        for row, item in enumerate(data):
            for col, val in enumerate(item):
                self.table_menu.setItem(row, col, QTableWidgetItem(str(val)))

    # ── Pilih menu dari tabel → isi form ──────────────────────
    def pilih_menu(self, row, column):
        nama  = self.table_menu.item(row, 1).text()
        harga = self.table_menu.item(row, 2).text()
        self.input_menu.setText(nama)
        self.input_harga.setText(harga)
        self.hitung_total()

    # ── Hitung total otomatis saat jumlah berubah ─────────────
    def hitung_total(self):
        harga  = int(self.input_harga.text() or 0)
        jumlah = self.spin_jumlah.value()
        self.input_total.setText(str(harga * jumlah))

    # ── Tambah item ke keranjang (belum ke DB) ────────────────
    def tambah_ke_keranjang(self):
        nama  = self.input_menu.text()
        harga = self.input_harga.text()

        if nama == "":
            Toast(self.window, "Pilih menu dulu!", "#e74c3c")
            return

        jumlah   = self.spin_jumlah.value()
        subtotal = int(harga) * jumlah

        # Jika menu sudah ada di keranjang → tambahkan jumlahnya
        for item in self.keranjang:
            if item["nama"] == nama:
                item["jumlah"]   += jumlah
                item["subtotal"] += subtotal
                Toast(self.window, f"{nama} (+{jumlah}) ditambahkan!", "#2ecc71")
                self.reset_form()
                self.update_btn_keranjang()
                return

        # Jika belum ada → tambah baru
        self.keranjang.append({
            "nama"    : nama,
            "harga"   : int(harga),
            "jumlah"  : jumlah,
            "subtotal": subtotal,
        })

        Toast(self.window, f"{nama} ditambahkan ke keranjang!", "#2ecc71")
        self.reset_form()
        self.update_btn_keranjang()

    # ── Update label tombol keranjang ─────────────────────────
    def update_btn_keranjang(self):
        total_item = sum(i["jumlah"] for i in self.keranjang)
        self.btn_keranjang.setText(f"🛒 LIHAT KERANJANG ({total_item})")

    # ── Buka halaman keranjang ────────────────────────────────
    def buka_keranjang(self):
        self.window.hide()
        self.cart = Cart(self.username, self.keranjang, self)

    def buka_riwayat(self):
        self.window.hide()
        self.riwayat = Riwayat(self.username, self)

    # ── Reset form setelah tambah ─────────────────────────────
    def reset_form(self):
        self.input_menu.clear()
        self.input_harga.clear()
        self.input_total.clear()
        self.spin_jumlah.setValue(1)
        self.table_menu.clearSelection()

    # ── Logout ────────────────────────────────────────────────
    def logout(self):
        if self.keranjang:
            if not KonfirmasiDialog.tanya(
                self.window, "Logout",
                "Keranjang kamu masih ada isi.\nYakin ingin logout? Pesanan akan dibatalkan."
            ):
                return

        self.window.close()
        self.next = Login()


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    database.setup_database()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Simpan ke variabel global agar tidak dihapus garbage collector
    global_ref = []

    _login = Login()
    global_ref.append(_login)

    sys.exit(app.exec())