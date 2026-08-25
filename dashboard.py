import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. KONFIGURASI HALAMAN & TEMA
# ==============================================================================
st.set_page_config(
    page_title="E-Commerce Public Data Dashboard",
    page_icon="📊",
    layout="wide"
)

sns.set_theme(style="darkgrid")

# ==============================================================================
# 2. MEMBACA DATA LANGSUNG DARI FILE ZIP DI GITHUB
# ==============================================================================
# TEMPELKAN BLOK KODE REVISI BARU INI:
import urllib.request
import zipfile
import io

@st.cache_data
def load_data_from_zip():
    # GANTI LINK DI BAWAH INI dengan link Raw Download ZIP dari GitHub
    zip_url = "https://github.com"
    
    req = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        zip_file_bytes = io.BytesIO(response.read())
        with zipfile.ZipFile(zip_file_bytes) as z:
            csv_filename = [f for f in z.namelist() if f.endswith('.csv')][0]
            with z.open(csv_filename) as f:
                df = pd.read_csv(f)
                
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    return df

try:
    with st.spinner("Sedang memuat data dari GitHub... Mohon tunggu sebentar."):
        main_df = load_data_from_zip()
except Exception as e:
    st.error(f"Gagal membaca file ZIP dari GitHub: {e}")
    st.stop()

# ==============================================================================
# 3. KOMPONEN SIDEBAR (FILTER)
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Panel Kontrol Filter")
    
    min_date = main_df['order_purchase_timestamp'].min().date()
    max_date = main_df['order_purchase_timestamp'].max().date()
    
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu Transaksi:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) & 
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
]

# ==============================================================================
# 4. KONTEN HALAMAN UTAMA
# ==============================================================================
st.title("✨ E-Commerce Public Data Analysis Dashboard")
st.markdown("Aplikasi dasbor interaktif untuk memantau performa penjualan, kepuasan, pengiriman, dan segmentasi pelanggan.")

col1, col2, col3 = st.columns(3)
with col1:
    total_orders = filtered_df['order_id'].nunique()
    st.metric(label="🛍️ Total Transaksi Berhasil", value=f"{total_orders:,}")
with col2:
    total_revenue = filtered_df['price'].sum()
    st.metric(label="💰 Total Pendapatan Operasional", value=f"R$ {total_revenue:,.2f}")
with col3:
    avg_review = filtered_df['review_score'].mean()
    st.metric(label="⭐ Rata-rata Skor Kepuasan", value=f"{avg_review:.2f} / 5.0")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Tren Bulanan", 
    "🏆 Performa Produk", 
    "⭐ Skor Ulasan", 
    "🚚 Durasi Logistik", 
    "💳 Pilihan Pembayaran", 
    "👥 Segmentasi Pelanggan (RFM)"
])

# ------------------------------------------------------------------------------
# TAB 1: TREN BULANAN
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Tren Total Penjualan dan Pendapatan Bulanan")
    
    monthly_data = filtered_df.groupby('order_month').agg({
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()
    monthly_data['order_month_str'] = monthly_data['order_month'].astype(str)
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 5))
    
    sns.lineplot(x="order_month_str", y="order_id", data=monthly_data, marker="o", color="#2A9D8F", linewidth=3, ax=ax)
    ax.set_title("Tren Volume Penjualan (Orders)", fontsize=12, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)
    
    sns.lineplot(x="order_month_str", y="price", data=monthly_data, marker="o", color="#E76F51", linewidth=3, ax=ax)
    ax.set_title("Tren Akumulasi Pendapatan (Revenue)", fontsize=12, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)
    
    st.pyplot(fig)

# ------------------------------------------------------------------------------
# TAB 2: PERFORMA PRODUK
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Kategori Produk Terlaris & Kurang Diminati (Top 5 & Bottom 5)")
    
    prod_col = 'product_category_name' if 'product_category_name' in filtered_df.columns else 'product_category_name_english'
    
    product_perf = filtered_df.groupby(prod_col).agg({
        'order_item_id': 'count'
    }).reset_index()
    
    top_5 = product_perf.sort_values(by='order_item_id', ascending=False).head(5)
    bottom_5 = product_perf.sort_values(by='order_item_id', ascending=True).head(5)
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 5))
    
    sns.barplot(x='order_item_id', y=prod_col, data=top_5, palette='viridis', ax=ax)
    ax.set_title("Top 5 Kategori Produk Tertinggi", fontsize=12, fontweight="bold")
    
    sns.barplot(x='order_item_id', y=prod_col, data=bottom_5, palette='rocket', ax=ax)
    ax.set_title("Bottom 5 Kategori Produk Terendah", fontsize=12, fontweight="bold")
    
    st.pyplot(fig)

# ------------------------------------------------------------------------------
# TAB 3: SKOR ULASAN
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Distribus Tingkat Kepuasan Berdasarkan Skor Ulasan")
    
    review_counts = filtered_df['review_score'].value_counts().sort_index().reset_index()
    review_counts.columns = ['review_score', 'count']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x='review_score', y='count', data=review_counts, palette='Blues_d', ax=ax)
    
    for index, row in review_counts.iterrows():
        ax.text(index, row['count'] + (row['count'] * 0.01), f"{int(row['count'])}", ha="center", fontweight="bold")
        
    ax.set_title("Sebaran Skor Kepuasan Transaksi Selesai", fontsize=12, fontweight="bold")
    st.pyplot(fig)

# ------------------------------------------------------------------------------
# TAB 4: DURASI LOGISTIK
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Rata-rata Waktu Pengiriman Barang Bulanan (Hari)")
    
    if 'delivery_days' in filtered_df.columns:
        delivery_data = filtered_df.groupby('order_month').agg({
            'delivery_days': 'mean'
        }).reset_index()
        delivery_data['order_month_str'] = delivery_data['order_month'].astype(str)
        
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.lineplot(x="order_month_str", y="delivery_days", data=delivery_data, marker="o", color="#457B9D", linewidth=3, ax=ax)
        
        overall_mean = filtered_df['delivery_days'].mean()
        ax.axhline(overall_mean, color="#E63946", linestyle="--", label=f"Rata-rata Keseluruhan: {overall_mean:.1f} Hari")
        
        ax.set_title("Tren Kecepatan Distribusi Logistik", fontsize=12, fontweight="bold")
        plt.xticks(rotation=45)
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Informasi analisis durasi pengiriman membutuhkan kolom 'delivery_days' dalam dataset Anda.")

# ------------------------------------------------------------------------------
# TAB 5: PILIHAN PEMBAYARAN
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("Dominasi Jenis Metode Pembayaran Transaksi")
    
    if 'payment_type' in filtered_df.columns:
        payment_counts = filtered_df['payment_type'].value_counts().reset_index()
        payment_counts.columns = ['payment_type', 'count']
        
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.barplot(x='count', y='payment_type', data=payment_counts, palette='crest', ax=ax)
        ax.set_title("Instrumen Finansial Utama Pilihan Pelanggan", fontsize=12, fontweight="bold")
        st.pyplot(fig)
    else:
        st.info("Informasi instrumen pembayaran membutuhkan kolom 'payment_type' dalam dataset Anda.")

# ------------------------------------------------------------------------------
# TAB 6: SEGMENTASI PELANGGAN (RFM)
# ------------------------------------------------------------------------------
with tab6:
    st.subheader("Identifikasi Pelanggan Terbaik via Metode Analisis RFM")
    
    recent_date = filtered_df['order_purchase_timestamp'].max() + dt.timedelta(days=1)
    
    rfm_df = filtered_df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()
    
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    top_5_recency = rfm_df.sort_values(by='recency', ascending=True).head(5)
    top_5_frequency = rfm_df.sort_values(by='frequency', ascending=False).head(5)
    top_5_monetary = rfm_df.sort_values(by='monetary', ascending=False).head(5)
    
    top_5_recency['customer_short'] = top_5_recency['customer_id'].str[:8]
    top_5_frequency['customer_short'] = top_5_frequency['customer_id'].str[:8]
    top_5_monetary['customer_short'] = top_5_monetary['customer_id'].str[:8]
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))
    
    # 1. Grafik Recency
    sns.barplot(y="recency", x="customer_short", data=top_5_recency, palette="BuGn_r", ax=ax)
    ax.set_title("Top 5 Customers by Recency (Days)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Customer ID (Short)")
    ax.tick_params(axis='x', rotation=30)
    
    # 2. Grafik Frequency
    sns.barplot(y="frequency", x="customer_short", data=top_5_frequency, palette="Oranges_r", ax=ax)
