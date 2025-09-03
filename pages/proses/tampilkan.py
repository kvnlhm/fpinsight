import streamlit as st
import mysql.connector
import pandas as pd

# Koneksi ke database MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="obat"
)

def add_data_to_database(kode, nama_obat):
    cursor = conn.cursor()
    query = "INSERT INTO kode_obat (kode, nama_obat) VALUES (%s, %s)"
    cursor.execute(query, (kode, nama_obat))
    conn.commit()
    cursor.close()

def load_data_from_database():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kode_obat")
    data = cursor.fetchall()
    cursor.close()
    return data


def show():
    st.title('Penamaan Kode Nama Obat')
    st.markdown("---")

    if st.button("Tambah"):
        st.session_state.current_page = 'tambah'
        st.experimental_rerun()
        
    # Tampilkan data dalam tabel
    data = load_data_from_database()
    if data:
        df = pd.DataFrame(data, columns=['Kode', 'Nama Obat'])
        st.write(df)

if __name__ == '__main__':
    main()
