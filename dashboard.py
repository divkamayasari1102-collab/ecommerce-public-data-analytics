import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os

# Konfigurasi dasar halaman aplikasi dasbor
st.set_page_config(
    page_title="E-Commerce Public Data Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# Mengatur tema visual seaborn agar rapi dan seragam
sns.set_theme(style="darkgrid")

# ID Google Drive yang sudah disesuaikan dengan berkas Anda
GOOGLE_DRIVE_FILE_ID = "1evo6EmgRhY90xH5aTY50pvB9vZbf-955" 

# Fungsi memuat data cerdas dengan fitur streaming dari Google Drive jika lokal kosong
@st.cache_data
def load_data_from_drive(file_id):
    local_path = "main_data_cached.csv"
    
    # Jika file belum terunduh di server Streamlit Cloud, lakukan pengunduhan otomatis
    if not os.path.exists(local_path):
        with st.spinner("Sedang mengunduh dataset dari Google Drive... Mohon tunggu sebentar."):
            # Menggunakan URL langsung Google Drive untuk download file besar dengan token konfirmasi
            download_url = f"https://google.com{file_id}"
            
            session = requests.Session()
            response = session.get(download_url, stream=True)
            
            # Mendeteksi apakah Google memberikan halaman konfirmasi pemindaian virus file besar
            token = None
            for key, value in response.cookies.items():
                if "download_warning" in key:
                    token = value
                    break
            
            if token:
                download_url = f"https://google.com{token}&id={file_id}"
                response = session.get(download_url, stream=True)
                
            # Menyimpan potongan data yang dialirkan ke dalam penyimpanan server lokal
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
                        
    # Membaca berkas menggunakan Pandas dari penyimpanan lokal server
    df = pd.read_csv(local_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    return df

# Memuat berkas data utama ke dalam dashboard
try:
    main_df = load_data_from_drive(GOOGLE_DRIVE_FILE_ID)
except Exception as e:
    st.error(f"Gagal mengunduh data dari Google Drive: {e}")
    st.markdown("Pastikan setelan file di Google Drive Anda sudah diatur ke **'Anyone with the link' (Siapa saja yang memiliki link)**.")
    st.stop()

# ==================== KOMPONEN SIDEBAR (FILTER) ====================
with st.sidebar:
    st.image("https://githubusercontent.com", width=180)
    st.title("🎛️ Panel Kontrol Filter")
    
    min_date = main_df["order_purchase_timestamp"].min().date()
    max_date = main_df["order_purchase_timestamp"].max().date()
    
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu Transaksi:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date) & 
    (main_df["order_purchase_timestamp"].dt.date <= end_date)
]

# ==================== KONTEN HALAMAN UTAMA ====================
st.title("📊 E-Commerce Public Dataset Analysis Dashboard")
st.markdown("Aplikasi dasbor interaktif untuk memantau performa penjualan, kepuasan, pengiriman, dan segmentasi pelanggan (Periode 2017 - 2018).")

# Tampilan Ringkasan Metrik Bisnis Utama (KPI Cards)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🛒 Total Transaksi Berhasil", value=f"{filtered_df['order_id'].nunique():,}")
with col2:
    st.metric(label="💰 Total Pendapatan Operasional", value=f"R$ {filtered_df['price'].sum():,.2f}")
with col3:
    st.metric(label="⭐ Rata-rata Skor Kepuasan", value=f"{filtered_df['review_score'].mean():.2f} / 5.0")

st.markdown("---")

# Mengelompokkan analisis ke dalam struktur tab navigasi yang rapi
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Tren Bulanan", 
    "🛍️ Performa Produk", 
    "⭐ Skor Ulasan", 
    "🚚 Durasi Logistik", 
    "💳 Pilihan Pembayaran",
    "🎯 Segmen Pelanggan (RFM)"
])

# ---- TAB 1: TREN BULANAN ----
with tab1:
    st.subheader("Tren Total Penjualan dan Pendapatan Bulanan")
    monthly_data = filtered_df.groupby('order_month').agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('price', 'sum')
    ).reset_index()
    monthly_data['order_month_str'] = monthly_data['order_month'].astype(str)
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 5))
    sns.lineplot(x="order_month_str", y="total_orders", data=monthly_data, marker="o", color="#2A9D8F", linewidth=3, ax=ax[0])
    ax[0].set_title("Tren Volume Penjualan (Orders)", fontsize=12, fontweight="bold")
    ax[0].tick_params(axis='x', rotation=45)
    
    sns.lineplot(x="order_month_str", y="total_revenue", data=monthly_data, marker="s", color="#E76F51", linewidth=3, ax=ax[1])
    ax[1].set_title("Tren Akumulasi Pendapatan (Revenue)", fontsize=12, fontweight="bold")
    ax[1].tick_params(axis='x', rotation=45)
    st.pyplot(fig)

# ---- TAB 2: PERFORMA PRODUK ----
with tab2:
    st.subheader("Kategori Produk Terlaris & Kurang Diminati (Top 5 & Bottom 5)")
    # Memastikan kolom product_category yang digunakan konsisten dengan notebook Anda
    prod_col = 'product_category' if 'product_category' in filtered_df.columns else 'product_category_name_english'
    
    product_perf = filtered_df.groupby(prod_col).agg(
        volume_penjualan=('order_item_id', 'count')
    ).reset_index()
    
    top_5 = product_perf.sort_values(by='volume_penjualan', ascending=False).head(5)
    bottom_5 = product_perf.sort_values(by='volume_penjualan', ascending=True).head(5)
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 5))
    sns.barplot(x="volume_penjualan", y=prod_col, data=top_5, palette="viridis", ax=ax[0])
    ax[0].set_title("Top 5 Kategori Produk Tertinggi", fontsize=12, fontweight="bold")
    
    sns.barplot(x="volume_penjualan", y=prod_col, data=bottom_5, palette="rocket", ax=ax[1])
    ax[1].set_title("Bottom 5 Kategori Produk Terendah", fontsize=12, fontweight="bold")
    st.pyplot(fig)

# ---- TAB 3: SKOR ULASAN ----
with tab3:
    st.subheader("Distribusi Tingkat Kepuasan Berdasarkan Skor Ulasan")
    review_counts = filtered_df['review_score'].dropna().value_counts().sort_index().reset_index()
    review_counts.columns = ['review_score', 'count']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x="review_score", y="count", data=review_counts, palette="Blues_d", ax=ax)
    for index, row in review_counts.iterrows():
        ax.text(x=index, y=row['count'] + (row['count']*0.01), s=f"{int(row['count']):,}", ha="center", fontweight="bold")
    ax.set_title("Sebaran Skor Kepuasan Transaksi Selesai", fontsize=12, fontweight="bold")
    st.pyplot(fig)

# ---- TAB 4: DURASI LOGISTIK ----
with tab4:
    st.subheader("Rata-rata Waktu Pengiriman Barang Bulanan (Hari)")
    delivery_data = filtered_df.groupby('order_month').agg(
        avg_delivery_days=('delivery_time_days', 'mean')
    ).reset_index()
    delivery_data['order_month_str'] = delivery_data['order_month'].astype(str)
    
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.lineplot(x="order_month_str", y="avg_delivery_days", data=delivery_data, marker="o", color="#457B9D", linewidth=3, ax=ax)
    overall_mean = delivery_data['avg_delivery_days'].mean()
    ax.axhline(overall_mean, color='#E63946', linestyle='--', label=f'Rata-rata Keseluruhan: {overall_mean:.1f} Hari')
    ax.set_title("Tren Kecepatan Distribusi Logistik", fontsize=12, fontweight="bold")
    plt.xticks(rotation=45)
    ax.legend()
    st.pyplot(fig)

# ---- TAB 5: PILIHAN PEMBAYARAN ----
with tab5:
    st.subheader("Dominasi Jenis Metode Pembayaran Transaksi")
    payment_counts = filtered_df['payment_type'].dropna().value_counts().reset_index()
    payment_counts.columns = ['payment_type', 'count']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x="count", y="payment_type", data=payment_counts, palette="crest", ax=ax)
    ax.set_title("Instrumen Finansial Utama Pilihan Pelanggan", fontsize=12, fontweight="bold")
    st.pyplot(fig)

# ---- TAB 6: SEGMENTASI PELANGGAN (RFM) ----
with tab6:
    st.subheader("Identifikasi Pelanggan Terbaik via Metode Analisis RFM")
    recent_date = filtered_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    rfm_df = filtered_df.groupby('customer_id').agg(
        last_purchase=('order_purchase_timestamp', 'max'),
        frequency=('order_id', 'nunique'),
        monetary=('price', 'sum')
    ).reset_index()
    
    rfm_df['recency'] = (recent_date - rfm_df['last_purchase']).dt.days
    rfm_df.drop(columns=['last_purchase'], inplace=True)
    
    top_5_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)
    top_5_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5)
    top_5_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    
    top_5_recency['customer_short'] = top_5_recency['customer_id'].str[:8]
    top_5_frequency['customer_short'] = top_5_frequency['customer_id'].str[:8]
    top_5_monetary['customer_short'] = top_5_monetary['customer_id'].str[:8]
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))
    sns.barplot(y="recency", x="customer_short", data=top_5_recency, palette="BuGn_r", ax=ax[0])
    ax[0].set_title("Top 5 Customers by Recency (Days)", fontsize=11, fontweight="bold")
    ax[0].set_xlabel("Customer ID (Short)")
    ax[0].tick_params(axis='x', rotation=30)
    
    sns.barplot(y="frequency", x="customer_short", data=top_5_frequency, palette="Oranges_r", ax=ax[1])