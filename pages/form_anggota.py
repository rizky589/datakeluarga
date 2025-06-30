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

# ===== FORM PENCARIAN BERDASARKAN NO KK =====
st.subheader("🔍 Cari Keluarga Berdasarkan No KK")
kk_cari = st.text_input("Masukkan No KK untuk mencari")

if kk_cari:
    try:
        df = ambil_semua_data()
        df['no kk'] = df['no kk'].str.replace("'", "")
        hasil = df[df['no kk'] == kk_cari.strip()]
        if not hasil.empty:
            st.success(f"Ditemukan {len(hasil)} anggota keluarga dengan No KK {kk_cari}:")
            for idx, row in hasil.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{row['nama']}** — NIK: `{row['nik']}` — {row['shdk']}, Umur: {row['umur']}")
                with col2:
                    if st.button(f"🖊️ Edit {idx}"):
                        st.session_state.no_kk = row['no kk']
                        st.session_state.nama_kk = row['nama kk']
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
                with col3:
                    if st.button(f"🗑️ Hapus {idx}"):
                        if hapus_berdasarkan_nik(row['nik']):
                            st.success(f"✅ Data {row['nama']} berhasil dihapus!")
                            st.rerun()
        else:
            st.warning("Tidak ditemukan data dengan No KK tersebut.")
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")

# === Tombol kembali ===
if st.button("🔙 Kembali ke Form Keluarga"):
    for key in ["anggota_ke", "jumlah_anggota", "anggota_data", "no_kk", "nama_kk"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
