import streamlit as st
import pandas as pd

def main():
    st.title("Data Transaksi")
    st.markdown("---")

    # Pastikan session state untuk halaman dan data ada
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'uploaded_filename' not in st.session_state:
        st.session_state.uploaded_filename = None  # Tambahkan session state untuk nama file yang diunggah

    file = st.file_uploader("", type=['xlsx'])

    if file is not None:
        data = pd.read_excel(file)
        st.session_state.data = data
        st.session_state.uploaded_filename = file.name  # Simpan nama file yang diunggah dalam session state

        st.session_state.data.index += 1 

    if st.session_state.data is not None:
        col1, col2, _ = st.columns([1, 3, 1])
        with col1:
            # Tambahkan input number untuk mengatur jumlah baris yang ditampilkan
            rows_to_display = st.number_input("Show", min_value=1, max_value=len(st.session_state.data), value=10)
        st.markdown("")
        st.markdown("")
        st.markdown("")

        # Menghitung start_row dan end_row berdasarkan halaman saat ini
        start_row = st.session_state.page * rows_to_display
        end_row = start_row + rows_to_display

        # Menempatkan tombol di bawah tabel
        col1, col2, col3, col4 = st.columns([1, 1, 4, 1])
        with col1:
            if st.button("Previous") and st.session_state.page > 0:
                st.session_state.page -= 1

        with col4:
            if st.button("Next") and end_row < len(st.session_state.data):
                st.session_state.page += 1

        # Perbarui start_row dan end_row setelah tombol ditekan
        start_row = st.session_state.page * rows_to_display
        end_row = start_row + rows_to_display

        # Menampilkan tabel yang diperbarui (hanya jika halaman berubah)
        st.table(st.session_state.data.iloc[start_row:end_row])

if __name__ == "__main__":
    main()
