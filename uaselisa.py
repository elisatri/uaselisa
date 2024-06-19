import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Fungsi untuk koneksi ke database MySQL
def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host='kubela.id',
            user='davis2024irwan',
            password='wh451n9m@ch1n3',
            database='aw',
            port=3306
        )
        if conn.is_connected():
            print("Connection to MySQL database successful")
            return conn
        else:
            print("Failed to connect to MySQL database")
            return None
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# Fungsi untuk mengambil data dari MySQL
def fetch_data(conn):
    query = """
        SELECT pc.productkey, pc.englishproductname, SUM(fs.salesamount) AS total_sales
        FROM dimproduct pc
        INNER JOIN factinternetsales fs ON pc.productkey = fs.productkey
        GROUP BY pc.productkey, pc.englishproductname
        ORDER BY total_sales DESC
    """
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        return pd.DataFrame()

# Aplikasi utama Streamlit
def main():
    st.title("Sales Revenue per Product Category")

    # Koneksi ke MySQL
    conn = get_mysql_connection()

    # Memeriksa apakah koneksi berhasil
    if conn:
        try:
            # Mengambil data
            data = fetch_data(conn)

            # Menutup koneksi
            conn.close()

            # Menampilkan data
            st.dataframe(data)

            # Menyiapkan data untuk plotting
            df = pd.DataFrame(data, columns=['productkey', 'englishproductname', 'total_sales'])
            
            # Membuat grafik batang
            fig, ax = plt.subplots(figsize=(10, 6))
            df.plot(x="englishproductname", y="total_sales", kind="bar", ax=ax, color="skyblue")
            ax.set_xlabel("Product")
            ax.set_ylabel("Sales Revenue")
            ax.set_title("Sales Revenue per Product")
            ax.set_xticklabels(df["englishproductname"], rotation=45, ha="right")
            
            # Menampilkan grafik di Streamlit
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Failed to connect to MySQL. Check connection parameters.")

# Menjalankan aplikasi
if __name__ == "__main__":
    main()
