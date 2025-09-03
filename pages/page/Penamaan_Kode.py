import streamlit as st
import mysql.connector
import pandas as pd
from pages.proses import tambah  # Impor modul tambah

# Koneksi ke database MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="obat"
)

def load_data_from_database():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kode, Nama 
        FROM kode_obat 
        ORDER BY SUBSTRING(kode, 1, 1), CAST(SUBSTRING(kode, 2) AS UNSIGNED)
    """)
    data = cursor.fetchall()
    cursor.close()
    return data

def main():
    if 'page_view' not in st.session_state:
        st.session_state.page_view = 'main'

    # Periksa jika halaman view adalah 'tambah'
    if st.session_state.page_view == 'tambah':
        tambah.main()  # Panggil fungsi main dari file tambah.py
        return

    st.title('Penamaan Kode Nama Obat')
    st.markdown("---")

    # Tombol untuk membuka halaman tambah data
    if st.button('Tambah Data'):
        st.session_state.page_view = 'tambah'
        st.experimental_rerun()

    # Tampilkan data dalam tabel
    data = load_data_from_database()
    if data:
        df = pd.DataFrame(data, columns=['Kode', 'Nama Obat'])

        col1, col2, _ = st.columns([1, 3, 1])  # Kolom kosong ditambahkan di antara untuk menjaga tombol "Next" di sebelah kanan

        # Mengambil input jumlah baris yang akan ditampilkan
        max_rows = len(df)
        default_value = min(10, max_rows)

        with col1:
            jumlah_baris = st.number_input('Show', min_value=1, max_value=max_rows, value=default_value)
        
        st.markdown("")
        st.markdown("")

        # Menyesuaikan indeks agar dimulai dari 1
        df.index = df.index + 1

        # Membuat state untuk menyimpan halaman saat ini
        if 'page' not in st.session_state:
            st.session_state.page = 0

        # Fungsi untuk menampilkan baris saat ini
        def get_current_page_data(df, page, jumlah_baris):
            # Pastikan variabel bertipe integer
            page = int(page)
            jumlah_baris = int(jumlah_baris)
            start = page * jumlah_baris
            end = start + jumlah_baris
            return df.iloc[start:end]

        # Menampilkan tabel dengan baris sesuai halaman saat ini
        current_data = get_current_page_data(df, st.session_state.page, jumlah_baris)

        # Tombol "Previous" dan "Next" yang sangat berdekatan
        col1, col2, col3, col4 = st.columns([1, 1, 4, 1])

        with col1:
            if st.button('Previous'):
                if st.session_state.page > 0:
                    st.session_state.page -= 1

        with col4:
            if (st.session_state.page + 1) * jumlah_baris < len(df):
                if st.button('Next'):
                    st.session_state.page += 1
        
        # Perbarui current_data setelah tombol ditekan
        current_data = get_current_page_data(df, st.session_state.page, jumlah_baris)

        # Menggunakan st.markdown untuk menampilkan tabel dengan tombol HTML
        st.markdown(
            """
            <style>
            .dataframe-container {
                width: 100%;
            }
            table {
                width: 100%;
            }
            thead th {
                text-align: center !important;
            }
            tbody th {
                text-align: center !important;
            }
            tbody td:nth-child(2) {
                text-align: left !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="dataframe-container">{current_data.to_html(escape=False)}</div>', unsafe_allow_html=True)
        

if __name__ == '__main__':
    main()
