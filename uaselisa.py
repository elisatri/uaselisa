import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# Fungsi untuk mengambil data penjualan per produk dari MySQL
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

# Fungsi untuk mengambil data promosi dari MySQL
def fetch_data_promotions(conn):
    query = """
        SELECT 
            p.productkey, 
            p.englishproductname, 
            pr.promotionkey,
            pr.englishpromotionname,
            SUM(s.salesamount) AS total_sales
        FROM 
            dimproduct p
        INNER JOIN 
            factinternetsales s ON p.productkey = s.productkey
        INNER JOIN 
            dimpromotion pr ON s.promotionkey = pr.promotionkey
        GROUP BY 
            p.productkey, 
            p.englishproductname,
            pr.promotionkey,
            pr.englishpromotionname
        ORDER BY 
            p.productkey, 
            pr.promotionkey;
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

# Fungsi untuk mengambil data geografis dari MySQL
def fetch_data_geography(conn):
    query = """
        SELECT 
            g.countryregioncode, 
            g.englishcountryregionname, 
            SUM(s.salesamount) AS total_sales
        FROM 
            dimgeography g
        INNER JOIN 
            factinternetsales s ON g.SalesTerritoryKey = s.SalesTerritoryKey
        GROUP BY 
            g.countryregioncode, g.englishcountryregionname
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

# Fungsi untuk mengambil data penjualan per produk dengan harga dari MySQL
def fetch_data_product_prices(conn):
    query = """
        SELECT 
            fs.salesordernumber,
            fs.salesorderlinenumber,
            dp.productkey,
            dp.englishproductname,
            dp.listprice,
            fs.orderquantity
        FROM 
            factinternetsales fs
        INNER JOIN 
            dimproduct dp ON fs.productkey = dp.productkey
            LIMIT 10000
    """
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        return pd.DataFrame()

# Aplikasi utama Streamlit
def main():
    st.title("Sales Analysis")

    # Koneksi ke MySQL
    conn = get_mysql_connection()

    # Memeriksa apakah koneksi berhasil
    if conn:
        try:
            # Mengambil data dari berbagai query
            data1 = fetch_data_sales_per_product(conn)
            data2 = fetch_data_sales_trend(conn)
            data3 = fetch_data_promotions(conn)
            data4 = fetch_data_geography(conn)
            data5 = fetch_data_product_prices(conn)

            # Menutup koneksi
            conn.close()

            # Bagian untuk menampilkan dan memplot data penjualan per produk
            st.subheader("Sales Revenue per Product Category")
            st.dataframe(data1)
            df1 = pd.DataFrame(data1, columns=['productkey', 'englishproductname', 'total_sales'])
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            df1.plot(x="englishproductname", y="total_sales", kind="bar", ax=ax1, color="skyblue")
            ax1.set_xlabel("Product")
            ax1.set_ylabel("Sales Revenue")
            ax1.set_title("Sales Revenue per Product (COMPARISON)")
            ax1.set_xticklabels(df1["englishproductname"], rotation=45, ha="right")
            st.pyplot(fig1)

            # Bagian untuk menampilkan dan memplot tren penjualan per tahun
            st.subheader("Sales Revenue Trend per Year")
            df2 = pd.DataFrame(data2, columns=['calendaryear', 'total_sales'])
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.plot(df2['calendaryear'], df2['total_sales'], marker='o', color='b', linestyle='-', linewidth=2)
            ax2.set_title('Sales Revenue Trend per Year (COMPARISON)')
            ax2.set_xlabel('Calendar Year')
            ax2.set_ylabel('Sales Revenue')
            ax2.grid(True)
            ax2.set_xticks(df2['calendaryear'])
            ax2.set_xticklabels(df2['calendaryear'], rotation=45)
            st.pyplot(fig2)

            # Bagian untuk menampilkan dan memplot data promosi
            st.subheader("Sales and Promotions Data")
            df3 = pd.DataFrame(data3, columns=['productkey', 'englishproductname', 'promotionkey', 'englishpromotionname', 'total_sales'])
            matrix_df = df3.pivot_table(index=['productkey', 'englishproductname'], columns=['promotionkey', 'englishpromotionname'], values='total_sales', fill_value=0)
            corr_matrix = matrix_df.corr()
            fig3, ax3 = plt.subplots(figsize=(12, 10))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, square=True, linewidths=.5, ax=ax3)
            ax3.set_title('Correlation Matrix between Product and Promotion (RELATIONSHIP)')
            ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45)
            ax3.set_yticklabels(ax3.get_yticklabels(), rotation=0)
            st.pyplot(fig3)

            # Bagian untuk menampilkan dan memplot data geografis
            st.subheader("Sales Revenue Distribution by Country")
            df4 = pd.DataFrame(data4, columns=['countryregioncode', 'englishcountryregionname', 'total_sales'])
            fig4 = px.choropleth(
                df4,
                locations="countryregioncode",
                color="total_sales",
                hover_name="englishcountryregionname",
                color_continuous_scale=px.colors.sequential.Plasma,
                labels={'total_sales':'Sales Revenue'},
                title="Sales Revenue Distribution by Country"
            )
            st.plotly_chart(fig4)

            # Bagian untuk menampilkan dan memplot data penjualan per produk dengan harga
            st.subheader("Sales Quantity and Price Range Analysis")
            df5 = pd.DataFrame(data5, columns=['salesordernumber', 'salesorderlinenumber', 'productkey', 'englishproductname', 'listprice', 'orderquantity'])
            bins = [0, 50, 100, 200, 500, 1000, 5000, 10000]
            labels = ['0-50', '50-100', '100-200', '200-500', '500-1000', '1000-5000', '5000-10000']
            df5['price_range'] = pd.cut(df5['listprice'], bins=bins, labels=labels, include_lowest=True)
            bar_data = df5.groupby('price_range')['orderquantity'].sum().reset_index()

            # Sankey data preparation
            sankey_data = df5.groupby(['englishproductname', 'price_range'])['orderquantity'].sum().reset_index()
            nodes = list(set(sankey_data['englishproductname'].tolist() + sankey_data['price_range'].tolist()))
            node_indices = {node: idx for idx, node in enumerate(nodes)}

            sankey_data['source'] = sankey_data['englishproductname'].map(node_indices)
            sankey_data['target'] = sankey_data['price_range'].map(node_indices)

            # Creating the combined figure
            fig5 = make_subplots(
                rows=2, cols=1,
                row_heights=[0.5, 0.5],
                vertical_spacing=0.1,
                specs=[[{"type": "bar"}], [{"type": "sankey"}]]
            )

            # Adding bar chart
            fig5.add_trace(
                go.Bar(x=bar_data['price_range'], y=bar_data['orderquantity'], name='Order Quantity'),
                row=1, col=1
            )

            # Adding Sankey diagram
            fig5.add_trace(
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=nodes,
                        color="blue"
                    ),
                    link=dict(
                        source=sankey_data['source'],
                        target=sankey_data['target'],
                        value=sankey_data['orderquantity']
                    )
                ),
                row=2, col=1
            )

            # Updating layout
            fig5.update_layout(
                title_text="Combined Bar Chart and Sankey Diagram",
                font_size=10,
                height=800
            )

            st.plotly_chart(fig5)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Failed to connect to MySQL. Check connection parameters.")

# Menjalankan aplikasi
if __name__ == "__main__":
    main()

