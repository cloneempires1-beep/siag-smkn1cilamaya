import streamlit as st
import sqlite3
import pandas as pd
import pytz
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Absensi SMKN 1 Cilamaya", layout="wide", page_icon="📝")

if 'page' not in st.session_state:
    st.session_state.page = "landing"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('absensi_sekolah.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS absensi
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tanggal TEXT, nama_guru TEXT, mapel TEXT, 
                  kelas TEXT, materi TEXT, status_siswa TEXT, status_kepsek TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, keterangan TEXT)''')
    
    # Data Guru SMKN 1 Cilamaya
    daftar_guru = [
        "Eman Hastopo, S.T", "Mashanudin, S.Pd", "Muhamad Nashrulloh, S.Pd",
        "Dadan Ramdana, S.Kom", "Siti Wardiyah, S.Si", "Asep Rida Rosmana, S.Pi",
        "Ratum, ST", "Irda Lulita Sari, S.Pd", "Syamsul Bahri, S.Pd",
        "Putri Pertiwi, S.Pi", "Rohmi Ikhtarini, S.Pd", "Rini Martyaning Diyah, S.Pi",
        "Moch.Suef, S.Pi", "Nunung Nurilah, S.Pd", "Hj. Diana Handi, M.Pd",
        "Enung Herayati, S.Pd", "Ema Susanti, S.Pd", "Harry Tovanny, S.Pd",
        "Rian Hidayat, ST", "Ary Dwijayanti, S.Pd", "Dinda Syifa Fauziah, S.Pd.I",
        "Azzah Fitriah, S.Pd", "Cahya Khomarudin, S.Kom, M.Pd", "Eni, S.Pd",
        "Gina Mardiana, S.Kom", "Ibnu Ubaidillah, S.Pd", "Marini, S.Pd",
        "Neneng Nurhasanah, S.Pd", "Teti Fatmawati F, S.Pd", "Triya Setyawati, S.Pd",
        "Wahyu Purnomo, S.Pd", "Dian Astuti, ST"
    ]
    
    for nama in daftar_guru:
        username = nama.split(',')[0].split(' ')[0].lower()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", 
                  (username, 'gurucilamaya', 'Guru', nama))

    # Data Kelas
    daftar_kelas = [
        "X APAT", "X APHP1", "X APHP2", "X TKRO 1", "X TKRO 2", "X TKRO 3", "X TKJ 1", "X TKJ 2", "X TP 1", "X TP 2",
        "XI APAT", "XI APHP1", "XI APHP2", "XI TKRO 1", "XI TKRO 2", "XI TKRO 3", "XI TKJ 1", "XI TKJ 2", "XI TP 1", "XI TP 2",
        "XII APAT", "XII APHP", "XII TKRO 1", "XII TKRO 2", "XII TKRO 3", "XII TKJ 1", "XII TKJ 2", "XII TKJ 3", "XII TP1", "XII TP2"
    ]
    
    for kelas in daftar_kelas:
        user_siswa = f"ketua_{kelas.replace(' ', '').lower()}"
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", 
                  (user_siswa, 'siswacilamaya', 'Siswa', kelas))

    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", 
              ('admin', 'admin123', 'Kepsek', 'Kepala Sekolah'))
    
    conn.commit()
    conn.close()

def get_waktu_wib():
    tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M")

def update_password(username, new_password):
    conn = sqlite3.connect('absensi_sekolah.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()

init_db()

# --- 3. ALUR HALAMAN ---

# LANDING PAGE
if st.session_state.page == "landing":
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        sub_col1, sub_col2, sub_col3 = st.columns([1.2, 1, 1.2])
        with sub_col2:
            try:
                st.image("image_d5260d.png", use_container_width=True)
            except:
                st.image("logoNSC.png", use_container_width=True)
        
        st.markdown("<h1 style='text-align: center; margin-top: 10px;'>SMKN 1 CILAMAYA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 20px;'>Sistem Informasi Absensi Guru (SIAG)</p>", unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚀 MULAI APLIKASI", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

# LOGIN
elif st.session_state.page == "login" and not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.title("🔐 Login")
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Masuk"):
                conn = sqlite3.connect('absensi_sekolah.db', check_same_thread=False)
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
                user = c.fetchone()
                conn.close()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_data = list(user)
                    st.session_state.page = "main"
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
        if st.button("⬅ Kembali"):
            st.session_state.page = "landing"
            st.rerun()

# DASHBOARD
elif st.session_state.logged_in:
    username_aktif, password_aktif, role, ket = st.session_state.user_data
    
    st.sidebar.title("SIAG Cilamaya")
    st.sidebar.write(f"User: **{ket}**")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.page = "landing"
        st.rerun()

# --- MODUL GURU (VERSI KETIK JAM MANUAL) ---
  if role == "Guru":
    from streamlit_js_eval import get_geolocation
    
    st.header(f"Panel Guru: {ket}")
    t1, t2, t3 = st.tabs(["📝 Input Absen", "📚 Riwayat & Materi", "🔐 Keamanan"])
    
    with t1:
        st.subheader("Form Absensi Harian")
        
        # Deteksi Lokasi
        st.markdown("### 📍 Verifikasi Lokasi")
        location = get_geolocation()
        
        if location:
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
            geo_string = f"{lat}, {lon}"
            st.success(f"Lokasi terdeteksi: {geo_string}")
        else:
            st.warning("Menunggu GPS... Pastikan izin lokasi (Allow) sudah diklik.")
            geo_string = None

        with st.form("absen_guru"):
            conn = sqlite3.connect('absensi_sekolah.db')
            # Pastikan kolom jam_ke dan lokasi ada
            try:
                conn.execute("ALTER TABLE absensi ADD COLUMN lokasi TEXT")
                conn.execute("ALTER TABLE absensi ADD COLUMN jam_ke TEXT")
                conn.commit()
            except: pass
            
            list_kelas = [r[0] for r in conn.execute("SELECT keterangan FROM users WHERE role='Siswa'").fetchall()]
            conn.close()
            
            kls = st.selectbox("Pilih Kelas", list_kelas)
            
            # --- INPUT JAM MANUAL ---
            jk = st.text_input("Mengajar di Jam Ke-", placeholder="Contoh: 1-4 atau 5-9")
            
            mpl = st.text_input("Mata Pelajaran")
            mtr = st.text_area("Materi Pembelajaran")
            
            submit_button = st.form_submit_button("Kirim Absensi")
            
            if submit_button:
                if not geo_string:
                    st.error("Gagal! Lokasi wajib dideteksi.")
                elif not jk or not mpl or not mtr:
                    st.error("Lengkapi semua data (Jam, Mapel, Materi).")
                else:
                    try:
                        conn = sqlite3.connect('absensi_sekolah.db')
                        c = conn.cursor()
                        
                        # Cek Duplikat berdasarkan teks yang diketik
                        tgl_hari_ini = get_waktu_wib().split(' ')[0]
                        c.execute("""
                            SELECT id FROM absensi 
                            WHERE nama_guru = ? 
                            AND kelas = ? 
                            AND jam_ke = ?
                            AND tanggal LIKE ?
                        """, (ket, kls, jk, f"{tgl_hari_ini}%"))
                        
                        if c.fetchone():
                            st.warning(f"⚠️ Anda sudah input absen kelas {kls} jam {jk} hari ini.")
                        else:
                            c.execute("""
                                INSERT INTO absensi (tanggal, nama_guru, mapel, kelas, materi, lokasi, jam_ke, status_siswa, status_kepsek) 
                                VALUES (?,?,?,?,?,?,?,?,?)
                            """, (get_waktu_wib(), ket, mpl, kls, mtr, geo_string, jk, 'Pending', 'Pending'))
                            conn.commit()
                            st.success(f"✅ Absensi jam {jk} berhasil dikirim!")
                        conn.close()
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")

        with t2:
            st.subheader("Riwayat Mengajar")
            conn = sqlite3.connect('absensi_sekolah.db')
            # Menampilkan kolom jam_ke di riwayat
            df = pd.read_sql_query("""
                SELECT tanggal, jam_ke as 'Jam Ke', kelas, mapel, materi, lokasi as '📍 Lokasi', status_siswa as 'Siswa', status_kepsek as 'Kepsek' 
                FROM absensi 
                WHERE nama_guru=? 
                ORDER BY tanggal DESC
            """, conn, params=(ket,))
            conn.close()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Belum ada riwayat.")
        
        # (Tab Keamanan/Ganti Password tetap sama)

        with t3:
            # (Bagian Ganti Password tetap sama seperti sebelumnya)
            st.subheader("Pengaturan Akun")
            with st.expander("Ganti Password"):
                new_p = st.text_input("Password Baru", type="password")
                confirm_p = st.text_input("Konfirmasi Password Baru", type="password")
                if st.button("Update Password"):
                    if new_p == confirm_p and new_p != "":
                        update_password(username_aktif, new_p)
                        st.success("✅ Password diperbarui!")

   # --- MODUL SISWA (VERSI BARU DENGAN JAM KE & LOKASI) ---
   elif role == "Siswa":
        st.header(f"Panel Ketua Kelas: {ket}")
        t1, t2, t3 = st.tabs(["✅ Validasi Guru", "📑 Rekap Guru Mengajar", "🔐 Keamanan"])
        
        with t1:
            st.subheader("Validasi Kehadiran Guru")
            conn = sqlite3.connect('absensi_sekolah.db')
            # Menampilkan data yang pending, menyertakan jam_ke dan lokasi
            df_v = pd.read_sql_query("""
                SELECT id, tanggal, jam_ke as 'Jam Ke', nama_guru as 'Nama Guru', 
                       mapel as 'Mapel', materi as 'Materi', lokasi 
                FROM absensi 
                WHERE kelas=? AND status_siswa='Pending'
            """, conn, params=(ket,))
            
            if not df_v.empty:
                st.write("Daftar guru yang belum divalidasi hari ini:")
                # Menampilkan data dalam bentuk kolom agar lebih rapi untuk Ketua Kelas
                for index, row in df_v.iterrows():
                    with st.expander(f"📌 Jam Ke-{row['Jam Ke']} | {row['Nama Guru']}"):
                        st.write(f"**Mata Pelajaran:** {row['Mapel']}")
                        st.write(f"**Materi:** {row['Materi']}")
                        if row['lokasi']:
                            st.caption(f"📍 Terdeteksi di koordinat: {row['lokasi']}")
                        
                        # Tombol konfirmasi langsung per baris (Tanpa ketik ID manual)
                        if st.button(f"Konfirmasi Kehadiran Jam {row['Jam Ke']}", key=f"v_{row['id']}"):
                            c = conn.cursor()
                            c.execute("UPDATE absensi SET status_siswa='Validated' WHERE id=?", (row['id'],))
                            conn.commit()
                            st.success(f"Berhasil validasi guru {row['Nama Guru']}!")
                            st.rerun()
            else:
                st.info("Tidak ada jadwal guru yang perlu divalidasi saat ini.")
            conn.close()

        with t2:
            st.subheader(f"Riwayat Guru di Kelas {ket}")
            conn = sqlite3.connect('absensi_sekolah.db')
            # Menampilkan riwayat lengkap termasuk Jam Ke
            df_rekap_siswa = pd.read_sql_query("""
                SELECT tanggal, jam_ke as 'Jam Ke', nama_guru as 'Nama Guru', 
                       mapel as 'Mapel', materi as 'Materi', status_siswa as 'Status' 
                FROM absensi 
                WHERE kelas=? 
                ORDER BY tanggal DESC
            """, conn, params=(ket,))
            conn.close()
            
            if not df_rekap_siswa.empty:
                st.dataframe(df_rekap_siswa, use_container_width=True)
            else:
                st.warning("Belum ada riwayat mengajar di kelas ini.")

        with t3:
            st.subheader("Pengaturan Akun")
            with st.expander("Ganti Password"):
                new_p = st.text_input("Password Baru", type="password")
                if st.button("Simpan Password"):
                    if new_p != "":
                        update_password(username_aktif, new_p)
                        st.success("✅ Password berhasil diperbarui!")
                    else:
                        st.error("Password tidak boleh kosong.")

    # --- MODUL KEPALA SEKOLAH (VERSI LENGKAP DENGAN GEOTAG & JAM) ---
    elif role == "Kepsek":
        st.header("Panel Administrasi Kepala Sekolah")
        t1, t2, t3 = st.tabs(["📋 Persetujuan", "📑 Rekap & Download", "🔐 Keamanan"])
        
        with t1:
            st.subheader("Antrean Persetujuan Absensi")
            conn = sqlite3.connect('absensi_sekolah.db')
            
            # Menampilkan kolom Jam Ke dan Lokasi agar Kepsek bisa cek validitas
            query_p = """
                SELECT id, tanggal, jam_ke as 'Jam Ke', nama_guru as 'Nama Guru', 
                       kelas as 'Kelas', mapel as 'Mapel', materi as 'Materi', lokasi as '📍 Lokasi'
                FROM absensi 
                WHERE status_siswa='Validated' AND status_kepsek='Pending'
            """
            df_p = pd.read_sql_query(query_p, conn)
            
            if not df_p.empty:
                st.write("Data berikut telah divalidasi oleh Ketua Kelas dan menunggu persetujuan Anda:")
                st.dataframe(df_p, use_container_width=True)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Setujui Semua", type="primary"):
                        c = conn.cursor()
                        c.execute("UPDATE absensi SET status_kepsek='Approved' WHERE status_siswa='Validated' AND status_kepsek='Pending'")
                        conn.commit()
                        st.success("Semua absensi telah disetujui!")
                        st.rerun()
            else:
                st.info("Tidak ada antrean persetujuan (semua sudah diproses atau belum divalidasi siswa).")
            conn.close()

        with t2:
            st.subheader("Pusat Data & Rekapitulasi")
            conn = sqlite3.connect('absensi_sekolah.db')
            
            # Ambil daftar guru untuk filter
            list_g = [r[0] for r in conn.execute("SELECT keterangan FROM users WHERE role='Guru'").fetchall()]
            
            col_a, col_b = st.columns(2)
            with col_a:
                pilih = st.selectbox("Filter Guru", ["Semua Guru"] + sorted(list_g))
            with col_b:
                # Opsi filter tambahan: Semua data atau hanya yang sudah Approved
                filter_status = st.radio("Status Data", ["Semua", "Hanya Approved"], horizontal=True)

            # Query dinamis berdasarkan filter
            query_final = "SELECT tanggal, jam_ke, nama_guru, kelas, mapel, materi, lokasi, status_siswa, status_kepsek FROM absensi WHERE 1=1"
            params = []
            
            if pilih != "Semua Guru":
                query_final += " AND nama_guru = ?"
                params.append(pilih)
            if filter_status == "Hanya Approved":
                query_final += " AND status_kepsek = 'Approved'"
                
            query_final += " ORDER BY tanggal DESC"
            
            df_final = pd.read_sql_query(query_final, conn, params=params)
            
            st.dataframe(df_final, use_container_width=True)
            
            # Tombol Download
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DOWNLOAD REKAP (CSV)", 
                data=csv, 
                file_name=f"rekap_cilamaya_{pilih}.csv", 
                mime='text/csv', 
                use_container_width=True
            )
            conn.close()

        with t3:
            st.subheader("Pengaturan Keamanan")
            with st.expander("Ganti Password Akun Kepsek"):
                new_p = st.text_input("Password Baru", type="password")
                confirm_p = st.text_input("Konfirmasi Password", type="password")
                if st.button("Update Password"):
                    if new_p == confirm_p and new_p != "":
                        update_password(username_aktif, new_p)
                        st.success("✅ Password berhasil diperbarui!")
                    else:
                        st.error("Password tidak cocok atau kosong.")
