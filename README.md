# E-Commerce Public Data Analytics Dashboard 📊

Dasbor interaktif ini dibangun menggunakan **Streamlit** untuk menganalisis data publik transaksi e-commerce. Proyek ini mencakup visualisasi tren penjualan bulanan, performa kategori produk, analisis skor ulasan kepuasan, efisiensi logistik pengiriman, instrumen pembayaran, hingga segmentasi profil pelanggan menggunakan metode RFM (*Recency, Frequency, Monetary*).

## 🚀 Fitur Utama Dashboard
- **Tren Penjualan Bulanan:** Memantau dinamika total volume pesanan dan perolehan omzet pendapatan bisnis.
- **Performa Produk:** Identifikasi kategori produk yang paling diminati (Top 5) dan kurang diminati (Bottom 5).
- **Analisis Kepuasan:** Sebaran skor ulasan bintang dari konsumen pasca-transaksi selesai.
- **Efisiensi Logistik:** Memantau tren durasi rata-rata kecepatan pengiriman barang dalam satuan hari.
- **Segmentasi RFM:** Mengelompokkan dan mengidentifikasi profil karakteristik pelanggan terbaik berdasarkan aktivitas belanja.

## 📦 Struktur Penyimpanan Data
Untuk mengatasi batas kapasitas maksimal unggahan file teks biasa di GitHub (maksimal 25 MB per file), berkas dataset utama berukuran ~60 MB dipisah secara lokal ke dalam 4 bagian file teks CSV sebelum digabungkan kembali dalam memori server via skrip kode Python:
- `main_data_part1.csv`
- `main_data_part2.csv`
- `main_data_part3.csv`
- `main_data_part4.csv`

## 🛠️ Cara Menjalankan Proyek di Komputer Lokal

### 1. Kloning Repositori
```bash
git clone https://github.com
cd ecommerce-public-data-analytics
```

### 2. Instalasi Library Dependensi
Pastikan Anda menginstal pustaka utama yang dibutuhkan sesuai dengan berkas `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi Streamlit
```bash
streamlit run dashboard.py
```

## 🧰 Teknologi Utama yang Digunakan
- **Streamlit** - Pembuatan antarmuka web dasbor interaktif secara instan.
- **Pandas** - Manipulasi tabel, pembersihan data, dan penggabungan dataset via `pd.concat`.
- **Matplotlib & Seaborn** - Pembuatan grafik visualisasi data yang estetis.
