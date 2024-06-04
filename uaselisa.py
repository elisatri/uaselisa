import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sqlalchemy import create_engine

# Database connection string
db_url = 'mysql+pymysql://username:password@localhost/dump-dw_aw'
engine = create_engine(db_url)

# SQL Query
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

# Execute SQL query and fetch data into DataFrame
try:
    df = pd.read_sql_query(sql_query, engine)
    
    # Create a bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(x="englishproductcategoryname", y="total_sales", kind="bar", ax=ax, color="skyblue")
    ax.set_xlabel("Kategori Produk")
    ax.set_ylabel("Pendapatan Penjualan")
    ax.set_title("Pendapatan Penjualan per Kategori Produk")
    ax.set_xticklabels(df["englishproductcategoryname"], rotation=45, ha="right")

    # Streamlit App
    st.title("Pendapatan Penjualan per Kategori Produk")

    # Display the chart in Streamlit
    st.pyplot(fig)

except Exception as e:
    st.error(f"Error fetching data from database: {e}")
