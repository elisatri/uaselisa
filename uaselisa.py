import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sqlalchemy import create_engine
import pymysql
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

# Fungsi untuk menjalankan skrip SQL pada database MySQL
def execute_sql_on_mysql(engine, sql_script):
    with engine.connect() as conn:
        sql_statements = sql_script.split(';')
        for statement in sql_statements:
            if statement.strip():
                conn.execute(statement)

# Konfigurasi koneksi database MySQL
db_user = 'root'
db_password = ''
db_host = 'localhost'
db_port = '3306'
db_name = 'dump-dw_aw'

# URL koneksi SQLAlchemy untuk MySQL
database_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

try:
    # Buat engine SQLAlchemy untuk koneksi MySQL
    engine = create_engine(database_url)
    
    # Mendapatkan isi file SQL dari GitHub
    sql_data = fetch_sql_from_github(github_url)
    
    # Jalankan skrip SQL pada database MySQL
    execute_sql_on_mysql(engine, sql_data)
    
    # Query SQL untuk mendapatkan data yang diperlukan
    sql_query = """
        SELECT 
            pc.productcategorykey,
            pc.englishproductcategoryname,
            SUM(is.salesamount) AS total_sales
        FROM 
            dimproductcategory pc
        INNER JOIN 
            factinternetsales is ON pc.productcategorykey = is.productcategorykey
        GROUP BY 
            pc.productcategorykey, pc.englishproductcategoryname
        ORDER BY 
            total_sales DESC
    """
    
    # Eksekusi query SQL dan ambil hasilnya ke dalam DataFrame
    df = pd.read_sql_query(sql_query, engine)
    
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
