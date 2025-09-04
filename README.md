FPInsight – Sistem Analisis Data Transaksi (FPGrowth & Aturan Asosiasi)

Ringkasan
- FPInsight adalah aplikasi web berbasis Streamlit untuk menambang pola pembelian (frequent itemsets) dan menghasilkan Aturan Asosiasi dari data transaksi menggunakan algoritma FPGrowth. Aplikasi menyediakan visualisasi FP-Tree, perhitungan metrik (support, confidence, lift), serta ekspor laporan ke PDF.

Fitur Utama
- Analisis FPGrowth: Temukan frequent itemsets dari data transaksi.
- Aturan Asosiasi: Hasilkan aturan dengan metrik kunci (support, confidence).
- Visualisasi FP-Tree: Gambar FP-Tree dan conditional FP-Tree.
- Dashboard Interaktif: Navigasi halaman analisis melalui UI Streamlit.
- Ekspor Laporan PDF: Cetak hasil analisis ke PDF profesional.
- Kontrol Akses Sederhana: Peran admin dan pimpinan (contoh kredensial ada di bawah).

Teknologi
- Python 3.10+
- Streamlit untuk UI
- Implementasi FPGrowth (modul kustom di `pages/proses/` dan paket pendukung di `requirements.txt`)
- Pandas, NumPy, scikit-learn, mlxtend untuk utilitas analisis
- FPDF/ReportLab untuk PDF
- Graphviz/Matplotlib untuk visualisasi

Struktur Proyek (ringkas)
```
app.py                      # Entry point Streamlit (navigasi halaman & login)
pages/page/*.py             # Halaman: Data_Transaksi, Penamaan_Kode, FPGrowth, Association Rules, Laporan
pages/proses/*.py           # Implementasi FPGrowth (FPTree, FPNode, FPGrowth), helper proses
utils/pdf_generator.py      # Generator laporan PDF
requirements.txt            # Dependensi Python
generated_pdfs/, reports/   # Output laporan
fp_tree*, conditional_fp_tree* # Output visualisasi
obat.db                     # Basis data contoh (opsional)
```

Persiapan Lingkungan
1) Buat dan aktifkan virtual environment (opsional namun disarankan)
```bash
python -m venv .venv
.venv\Scripts\activate    # Windows PowerShell
# source .venv/bin/activate  # macOS/Linux
```

2) Instal dependensi
```bash
pip install -r requirements.txt
```

Catatan dependensi/OS:
- Graphviz mungkin perlu diinstal di OS agar visualisasi berjalan (Windows: instal Graphviz dan tambahkan ke PATH).
- Direktori output seperti `generated_pdfs/`, `reports/` akan dibuat saat runtime bila diperlukan.

Menjalankan Aplikasi
```bash
streamlit run app.py
```

Login (contoh kredensial default)
- admin: admin123
- pimpinan: pimpinan123

Cara Pakai Singkat
1) Masuk dengan akun di atas.
2) Buka halaman Data_Transaksi / Penamaan_Kode untuk memuat/menyiapkan data.
3) Jalankan Perhitungan_FPGrowth untuk menambang frequent itemsets.
4) Lihat hasil dan metrik di Association_Rules.
5) Ekspor laporan melalui halaman Laporan (tersimpan di `generated_pdfs/` atau `reports/`).

Dataset/Database
- File contoh basis data: `obat.db` (abaikan di Git, gunakan sample/skrip impor jika perlu).

Build/Packaging (opsional)
- Untuk deployment lokal, cukup jalankan perintah Streamlit di atas.
- Untuk server, rekomendasi gunakan virtual environment terpisah dan `streamlit run app.py` di service manager.

Kontribusi
- Pull request dan issue dipersilakan. Mohon jelaskan perubahan dan sertakan langkah uji.

Lisensi
- Tentukan lisensi yang Anda inginkan (mis. MIT). Tambahkan file LICENSE bila sudah dipilih.

Kontak
- Nama Proyek: FPInsight
- Deskripsi: Sistem Analisis Data Transaksi (FPGrowth & Aturan Asosiasi)

