import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import sqlite3
import requests

# URL raw file SQL di GitHub
github_url = 'https://raw.githubusercontent.com/elisatri/uaselisa/main/dump-dw_aw-202403050806.sql'

# Fungsi untuk mendapatkan isi file SQL dari GitHub
def fetch_sql_from_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise ValueError(f"Failed to fetch SQL file from GitHub. Status code: {response.status_code}")

# Mendapatkan isi file SQL dari GitHub
try:
    sql_data = fetch_sql_from_github(github_url)
    
    # Membuat koneksi ke database SQLite dalam memori
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Eksekusi skrip SQL untuk membuat dan memasukkan data ke dalam database SQLite
    sql_statements = sql_data.split(';')
    for statement in sql_statements:
        if statement.strip():
            try:
                cursor.execute(statement)
            except sqlite3.OperationalError as e:
                print(f"Error executing statement: {statement}\n{e}")
    
    # Query SQL untuk mendapatkan data yang diperlukan
    sql_query = """
        SELECT pc.productkey, pc.englishproductname, SUM(fs.salesamount) AS total_sales FROM dimproduct pc 
        INNER JOIN factinternetsales fs ON pc.productkey = fs.productkey GROUP BY pc.productkey, pc.englishproductname ORDER BY total_sales DESC
    """
    
    # Eksekusi query SQL dan ambil hasilnya ke dalam DataFrame
    df = pd.read_sql_query(sql_query, conn)
    
    # Buat grafik batang
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(x="englishproductcategoryname", y="total_sales", kind="bar", ax=ax, color="skyblue")
    ax.set_xlabel("Kategori Produk")
    ax.set_ylabel("Pendapatan Penjualan")
    ax.set_title("Pendapatan Penjualan per Kategori Produk")
    ax.set_xticklabels(df["englishproductcategoryname"], rotation=45, ha="right")
    
    # Aplikasi Streamlit
    st.title("Pendapatan Penjualan per Kategori Produk")
    
    # Tampilkan grafik di Streamlit
    st.pyplot(fig)

except Exception as e:
    st.error(f"Error: {e}")
