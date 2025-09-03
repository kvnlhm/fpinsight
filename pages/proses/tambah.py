import streamlit as st
import mysql.connector

# Koneksi ke database MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="obat"
)

def add_data_to_database(kode, Nama):
    cursor = conn.cursor()
    query = "INSERT INTO kode_obat (kode, Nama) VALUES (%s, %s)"
    cursor.execute(query, (kode, Nama))
    conn.commit()
    cursor.close()

def main():
    st.header('Tambah Data Kode Obat', divider='grey')

    # Tampilkan form untuk menambah data
    with st.form(key='add_data_form'):
        kode = st.text_input('Kode')
        Nama = st.text_input('Nama Obat')
        submit_button = st.form_submit_button(label='Simpan')

    if submit_button:
        add_data_to_database(kode, Nama)
        st.success('Data berhasil ditambahkan!')

        # Kembali ke halaman utama setelah menambahkan data
        st.session_state.page_view = 'main'
        st.experimental_rerun()

if __name__ == '__main__':
    main()
