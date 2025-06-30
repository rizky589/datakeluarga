import streamlit as st
from datetime import date
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ======== FUNGSI SIMPAN & CEK DUPLIKAT =========
def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Ambil kredensial dari secrets.toml
    service_account_info = dict(st.secrets["google_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    spreadsheet_id = "1LOv15OJL__vKiok8qmJqPGt4Je4nmxVSV0_a0ed8L5w"
    sheet = client.open_by_key(spreadsheet_id).worksheet("Keluarga")
    return sheet

def is_no_kk_duplicate(no_kk):
    sheet = connect_sheet()
    existing_data = [str(cell).strip() for cell in sheet.col_values(2)]  # Kolom B = No KK
    return str(no_kk).strip() in existing_data

def simpan_ke_sheets(data):
    sheet = connect_sheet()
    sheet.append_row([""] + data, value_input_option="USER_ENTERED")

# ========== UI FORM ============
st.set_page_config(page_title="Form Pendataan Kepala Keluarga", layout="centered")
st.title("📝 Form Pendataan Kepala Keluarga")

with st.form("form_kepala_keluarga", clear_on_submit=True):
    st.subheader("📍 Wilayah")
    st.text_input("Provinsi", value="Sumatera Utara", disabled=True)
    st.text_input("Kabupaten", value="Labuhanbatu Utara", disabled=True)
    st.text_input("Kecamatan", value="Kualuh Hulu", disabled=True)
    st.text_input("Desa", value="MambangMuda", disabled=True)

    dusun = st.text_input("Dusun")
    alamat = st.text_area("Alamat")

    st.subheader("🧑‍💼 Keterangan Petugas")
    nama_petugas = st.text_input("Nama Petugas Pendataan")
    nama_petugas1 = st.text_input("Nama Petugas Pengawas")
    tanggal_input = st.date_input("Tanggal Pendataan", value=date.today())

    st.subheader("👨‍👩‍👧‍👦 Data Keluarga")
    noKK = st.text_input("No KK", max_chars=16)
    nama_KepalaKeluarga = st.text_input("Nama Kepala Keluarga")
    jumlah_anggota = st.number_input("Jumlah Anggota Keluarga", min_value=1, step=1)

    simpan = st.form_submit_button("💾 Simpan & Lanjut")

# ========== LOGIKA SIMPAN ============
if simpan:
    if not all([noKK, nama_KepalaKeluarga, dusun, alamat, nama_petugas, nama_petugas1]):
        st.warning("⚠️ Semua kolom wajib diisi. Pastikan tidak ada yang kosong.")
    elif not noKK.isdigit() or len(noKK) != 16:
        st.error("❌ No KK harus 16 digit angka.")
    elif is_no_kk_duplicate(noKK):
        st.error("❌ No KK ini sudah pernah diinput! Harap cek kembali.")
        st.stop()
    else:
        for key in ["anggota_ke", "jumlah_anggota", "anggota_data", "edit_index"]:
            st.session_state.pop(key, None)

        st.session_state.no_kk = noKK
        st.session_state.nama_kk = nama_KepalaKeluarga
        st.session_state.jumlah_anggota = jumlah_anggota

        data_keluarga = [
            noKK,
            nama_KepalaKeluarga,
            dusun,
            alamat,
            nama_petugas,
            nama_petugas1,
            tanggal_input.strftime('%d/%m/%Y'),
            jumlah_anggota
        ]

        try:
            simpan_ke_sheets(data_keluarga)
            st.success("✅ Data keluarga berhasil disimpan ke Google Sheets.")
            st.balloons()
            st.switch_page("pages/form_anggota.py")
        except Exception as e:
            st.error(f"❌ Gagal menyimpan ke Google Sheets: {e}")
