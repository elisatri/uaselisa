import streamlit as st
import pymysql
import pandas as pd

# Fungsi untuk koneksi ke database
@st.cache(allow_output_mutation=True)
def connect_db():
    conn = pymysql.connect(
        host='127.0.0.1',  # Ganti dengan host Anda
        port=3306,          # Port default MySQL
        user='root',        # Ganti dengan username Anda
        passwd='',          # Ganti dengan password Anda
        db='dump-dw_aw'  # Ganti dengan nama database Anda
    )
    return conn

try:
    # Mendapatkan koneksi ke database
    conn = connect_db()

    # Query database
    query = "SELECT * FROM nama_tabel"
    df = pd.read_sql(query, con=conn)

    # Menampilkan hasil query
    st.write(df)

    # Menutup koneksi database
    conn.close()

except pymysql.MySQLError as e:
    st.error(f"Error: {e}")
