import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import mysql.connector

# Fungsi untuk mendapatkan koneksi ke MySQL
def get_mysql_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='dump-dw_aw'
    )
    return conn

# Query untuk mendapatkan data
def fetch_data(conn):
    query = """
        SELECT pc.productkey, pc.englishproductname, SUM(fs.salesamount) AS total_sales FROM dimproduct pc 
        INNER JOIN factinternetsales fs ON pc.productkey = fs.productkey GROUP BY pc.productkey, pc.englishproductname ORDER BY total_sales DESC
    """
    df = pd.read_sql(query, conn)
    return df

# Koneksi ke MySQL
conn = get_mysql_connection()

# Streamlit App
st.title("Pendapatan Penjualan per Kategori Produk")

# Fetch data
try:
    df = fetch_data(conn)
    conn.close()

    # Buat grafik batang
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(x="englishproductcategoryname", y="total_sales", kind="bar", ax=ax, color="skyblue")
    ax.set_xlabel("Kategori Produk")
    ax.set_ylabel("Pendapatan Penjualan")
    ax.set_title("Pendapatan Penjualan per Kategori Produk")
    ax.set_xticklabels(df["englishproductcategoryname"], rotation=45, ha="right")

    # Tampilkan grafik di Streamlit
    st.pyplot(fig)

except mysql.connector.Error as e:
    st.error(f"Error connecting to MySQL: {e}")

except Exception as e:
    st.error(f"Error: {e}")
