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
def fetch_data_sales_per_product(conn):
    query = """
        SELECT pc.productkey, pc.englishproductname, SUM(fs.salesamount) AS total_sales
        FROM dimproduct pc
        INNER JOIN factinternetsales fs ON pc.productkey = fs.productkey
        GROUP BY pc.productkey, pc.englishproductname
        ORDER BY total_sales DESC
        LIMIT 25
    """
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        return pd.DataFrame()

# Fungsi untuk mengambil data tren penjualan per tahun dari MySQL
def fetch_data_sales_trend(conn):
    query = """
        SELECT t.calendaryear, SUM(s.salesamount) AS total_sales
        FROM dimtime t
        INNER JOIN factinternetsales s ON t.timekey = s.orderdatekey
        GROUP BY t.calendaryear
        ORDER BY t.calendaryear;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data
    except mysql.connector.Error as e:
        print(f"Error fetching data from MySQL: {e}")
        return []

# Aplikasi utama Streamlit
def main():
    st.title("Sales Analysis")

    # Koneksi ke MySQL
    conn = get_mysql_connection()

    # Memeriksa apakah koneksi berhasil
    if conn:
        try:
            # Mengambil data penjualan per produk
            data1 = fetch_data_sales_per_product(conn)
            # Mengambil data tren penjualan per tahun
            data2 = fetch_data_sales_trend(conn)

            # Menutup koneksi
            conn.close()

            # Menampilkan data penjualan per produk
            st.subheader("Sales Revenue per Product Category")
            st.dataframe(data1)

            # Menyiapkan data untuk plotting
            df1 = pd.DataFrame(data1, columns=['productkey', 'englishproductname', 'total_sales'])
            
            # Membuat grafik batang
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            df1.plot(x="englishproductname", y="total_sales", kind="bar", ax=ax1, color="skyblue")
            ax1.set_xlabel("Product")
            ax1.set_ylabel("Sales Revenue")
            ax1.set_title("Sales Revenue per Product (COMPARISON)")
            ax1.set_xticklabels(df1["englishproductname"], rotation=45, ha="right")

            # Menampilkan grafik di Streamlit
            st.pyplot(fig1)

            # Menyiapkan data untuk plotting tren penjualan per tahun
            df2 = pd.DataFrame(data2, columns=['calendaryear', 'total_sales'])
            
            # Membuat grafik tren penjualan
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.plot(df2['calendaryear'], df2['total_sales'], marker='o', color='b', linestyle='-', linewidth=2)
            ax2.set_title('Sales Revenue Trend per Year (COMPARISON)')
            ax2.set_xlabel('Calendar Year')
            ax2.set_ylabel('Sales Revenue')
            ax2.grid(True)
            ax2.set_xticks(df2['calendaryear'])
            ax2.set_xticklabels(df2['calendaryear'], rotation=45)

            # Menampilkan grafik di Streamlit
            st.pyplot(fig2)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Failed to connect to MySQL. Check connection parameters.")

# Menjalankan aplikasi
if __name__ == "__main__":
    main()
