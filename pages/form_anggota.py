import streamlit as st
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Fungsi hitung umur otomatis
def hitung_umur(tgl_lahir):
    today = date.today()
    return today.year - tgl_lahir.year - ((today.month, today.day) < (tgl_lahir.month, tgl_lahir.day))

# Koneksi ke Google Sheets
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
    client = gspread.authorize(creds)
    return client.open_by_key("1LOv15OJL__vKiok8qmJqPGt4Je4nmxVSV0_a0ed8L5w").worksheet("Anggota")

def cek_nik_ganda(nik_baru):
    sheet = get_sheet()
    existing_data = sheet.col_values(4)[1:]
    return nik_baru in existing_data

def simpan_ke_sheets(data):
    sheet = get_sheet()
    sheet.append_row([""] + data, value_input_option="USER_ENTERED")

def ambil_semua_data():
    sheet = get_sheet()
    records = sheet.get_all_values()
    df = pd.DataFrame(records[1:], columns=[col.lower() for col in records[0]])
    return df

def hapus_berdasarkan_nik(nik):
    sheet = get_sheet()
    col = sheet.col_values(4)
    for idx, val in enumerate(col):
        if val.strip() == nik:
            sheet.delete_rows(idx + 1)
            return True
    return False

def update_berdasarkan_nik(nik_lama, data_baru):
    sheet = get_sheet()
    col = sheet.col_values(4)
    for idx, val in enumerate(col):
        if val.strip() == nik_lama:
            sheet.delete_rows(idx + 1)
            sheet.insert_row([""] + data_baru, index=idx + 1, value_input_option="USER_ENTERED")
            return True
    return False

st.set_page_config(page_title="Form Anggota Keluarga", layout="centered")
st.title("🧝 Form Anggota Keluarga")

if "no_kk" not in st.session_state or "nama_kk" not in st.session_state:
    st.warning("⚠️ Silakan isi Form Keluarga terlebih dahulu.")
    st.stop()

if "anggota_ke" not in st.session_state:
    st.session_state.anggota_ke = 1
if "jumlah_anggota" not in st.session_state:
    st.session_state.jumlah_anggota = 1
if "anggota_data" not in st.session_state:
    st.session_state.anggota_data = []
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

anggota_ke = st.session_state.anggota_ke
jumlah_total = st.session_state.jumlah_anggota
st.subheader(f"👨‍👩‍👧‍👦 Anggota Keluarga ke-{anggota_ke} dari {jumlah_total}")
st.text(f"Nomor KK: {st.session_state.no_kk}")

with st.form("form_anggota", clear_on_submit=not st.session_state.edit_mode):
    nama = st.text_input("📝 Nama", value=st.session_state.get("edit_nama", ""))
    nik = st.text_input("🆔 NIK (16 digit, unik)", max_chars=16, value=st.session_state.get("edit_nik", ""))
    keberadaan = st.selectbox("📍 Keberadaan", ["Domisili Sesuai KK", "Tidak Sesuai KK", "Meninggal", "Lainnya"], index=["Domisili Sesuai KK", "Tidak Sesuai KK", "Meninggal", "Lainnya"].index(st.session_state.get("edit_keberadaan", "Domisili Sesuai KK")))
    tanggal_lahir = st.date_input("📆 Tanggal Lahir", value=st.session_state.get("edit_tgl", date(2000, 1, 1)), min_value=date(1945, 1, 1), max_value=date.today())
    umur = hitung_umur(tanggal_lahir)
    st.success(f"🎂 Umur: {umur} tahun")
    jk = st.selectbox("🚻 Jenis Kelamin", ["Laki-laki", "Perempuan"], index=["Laki-laki", "Perempuan"].index(st.session_state.get("edit_jk", "Laki-laki")))
    ijazah = st.selectbox("🎓 Ijazah Tertinggi", ["Tidak tamat SD", "SD", "SMP", "SMA", "Perguruan Tinggi"], index=["Tidak tamat SD", "SD", "SMP", "SMA", "Perguruan Tinggi"].index(st.session_state.get("edit_ijazah", "SD")))
    status = st.selectbox("💍 Status Perkawinan", ["Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati"], index=["Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati"].index(st.session_state.get("edit_status", "Belum Kawin")))
    status_pekerjaan = st.selectbox("📌 Status Pekerjaan", ["Tidak Bekerja", "Berusaha Sendiri", "Buruh", "Pegawai"], index=["Tidak Bekerja", "Berusaha Sendiri", "Buruh", "Pegawai"].index(st.session_state.get("edit_status_pekerjaan", "Tidak Bekerja")))
    pekerjaan = st.text_input("💼 Pekerjaan Utama", value=st.session_state.get("edit_pekerjaan", ""))
    lapangan = st.selectbox("🏢 Lapangan Usaha", ["Pertanian", "Industri", "Perdagangan", "Pemerintahan", "Pendidikan", "Kesehatan", "Lainnya"], index=["Pertanian", "Industri", "Perdagangan", "Pemerintahan", "Pendidikan", "Kesehatan", "Lainnya"].index(st.session_state.get("edit_lapangan", "Pertanian")))
    shdk = st.selectbox("👪 SHDK", ["Kepala Rumah Tangga", "Istri", "Anak", "Cucu", "Orang tua", "Lainnya"], index=["Kepala Rumah Tangga", "Istri", "Anak", "Cucu", "Orang tua", "Lainnya"].index(st.session_state.get("edit_shdk", "Anak")))
    simpan = st.form_submit_button("📂 Simpan")

if simpan:
    if not all([nama, nik, keberadaan, jk, ijazah, status, status_pekerjaan, pekerjaan, lapangan, shdk]):
        st.warning("⚠️ Semua kolom wajib diisi!")
    elif not nik.isdigit() or len(nik) != 16:
        st.warning("⚠️ NIK harus 16 digit angka!")
    elif cek_nik_ganda(nik) and not st.session_state.edit_mode:
        st.error("❌ NIK sudah pernah diinput!")
    else:
        data = [
            f"'{str(st.session_state.no_kk)}".strip(),
            st.session_state.nama_kk,
            nama,
            f"'{nik}",
            keberadaan,
            tanggal_lahir.strftime('%d/%m/%Y'),
            umur,
            jk,
            ijazah,
            status,
            status_pekerjaan,
            pekerjaan,
            lapangan,
            shdk
        ]
        try:
            if st.session_state.edit_mode:
                update_berdasarkan_nik(st.session_state.edit_nik, data)
                st.success("✅ Data berhasil diupdate!")
                st.session_state.edit_mode = False
                for k in list(st.session_state.keys()):
                    if k.startswith("edit_"):
                        del st.session_state[k]
            else:
                simpan_ke_sheets(data)
                st.success("✅ Data berhasil disimpan!")
                st.session_state.anggota_data.append(data)
                if st.session_state.anggota_ke < st.session_state.jumlah_anggota:
                    st.session_state.anggota_ke += 1
            st.rerun()
        except Exception as e:
            st.error(f"❌ Gagal menyimpan: {e}")

try:
    df = ambil_semua_data()
    df['no kk'] = df['no kk'].str.replace("'", "")
    df = df[df['no kk'] == str(st.session_state.no_kk)]
    if not df.empty:
        st.write("## ✏️ Daftar Anggota Saat Ini:")
        for _, row in df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{row['nama']}** — NIK: `{row['nik']}` — {row['shdk']}, Umur: {row['umur']}")
            with col2:
                if st.button("🖊️ Edit", key=f"edit_{row['nik']}"):
                    st.session_state.edit_mode = True
                    st.session_state.edit_nik = row['nik']
                    st.session_state.edit_nama = row['nama']
                    st.session_state.edit_keberadaan = row['keberadaan']
                    st.session_state.edit_tgl = datetime.strptime(row['tanggal lahir'], "%d/%m/%Y").date()
                    st.session_state.edit_jk = row['jenis kelamin']
                    st.session_state.edit_ijazah = row['ijazah']
                    st.session_state.edit_status = row['status perkawinan']
                    st.session_state.edit_status_pekerjaan = row['status pekerjaan']
                    st.session_state.edit_pekerjaan = row['pekerjaan utama']
                    st.session_state.edit_lapangan = row['lapangan usaha']
                    st.session_state.edit_shdk = row['shdk']
                    st.rerun()
                if st.button("🗑️ Hapus", key=f"hapus_{row['nik']}"):
                    if hapus_berdasarkan_nik(row['nik']):
                        st.success(f"✅ Data {row['nama']} berhasil dihapus!")
                        st.rerun()
    else:
        st.info("Belum ada data untuk ditampilkan.")
except Exception as e:
    st.error(f"Gagal menampilkan data: {e}")

if st.button("🔙 Kembali ke Form Keluarga"):
    for key in ["anggota_ke", "jumlah_anggota", "anggota_data", "no_kk", "nama_kk"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
