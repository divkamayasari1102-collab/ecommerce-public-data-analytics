# 📊 E-Commerce Public Dataset Analysis Project

Proyek ini merupakan portofolio analisis data ujung ke ujung (*end-to-end*) menggunakan **E-Commerce Public Dataset**. Analisis difokuskan pada pengecekan kualitas data, eksplorasi data terarah, visualisasi pemecahan 5 masalah bisnis utama, serta pembuatan aplikasi dasbor interaktif berbasis web menggunakan Streamlit.

> 💡 **Informasi Manajemen Data Besar:** Karena ukuran dataset gabungan akhir melampaui ambang batas maksimum unggahan berkas tunggal di repositori GitHub, proyek ini dirancang secara modern agar dasbor Streamlit mengalirkan data (*streaming data*) secara langsung dan dinamis dari penyimpanan awan Google Drive publik menggunakan ID file yang aman saat pertama kali diakses.

## ✨ Struktur Direktori Proyek GitHub

```text
submission/
├── dashboard/
│   └── dashboard.py
├── data/
│   └── E-Commerce Public Dataset.zip
├── notebook.ipynb
├── README.md
└── requirements.txt
```

## 🛠️ Langkah Menjalankan Aplikasi di Komputer Lokal

### 1. Membuat Lingkungan Kerja Virtual (Virtual Environment)
Jalankan perintah ini pada terminal atau command prompt komputer Anda:

```bash
# Pengguna Windows
python -m venv venv
venv\Scripts\activate

# Pengguna macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Memasang Seluruh Pustaka Dependensi (Libraries)
Pasang semua dependensi utama yang tercantum di dalam file requirements.txt:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi Web Dashboard Streamlit
Pastikan komputer Anda terhubung dengan internet agar modul aplikasi dapat mengunduh data dari awan secara otomatis pada pemanggilan pertama, kemudian eksekusi perintah berikut:

```bash
streamlit run dashboard/dashboard.py
```

Setelah perintah dijalankan, peramban (*browser*) Anda akan terbuka secara otomatis mengarah ke alamat lokal default aplikasi: http://localhost:8501