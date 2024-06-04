import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sqlalchemy import create_engine

# Read SQL data from file
with open("dump-dw_aw-202403050806.sql", "r") as f:
    sql_data = f.read()

# Create an in-memory SQLite engine using SQLAlchemy
engine = create_engine("sqlite:///:memory:")

# Execute SQL queries and load data into DataFrames
with engine.connect() as conn:
    conn.execute(sql_data)
    product_categories_df = pd.read_sql("SELECT * FROM dimproductcategory", conn)
    internet_sales_df = pd.read_sql("SELECT * FROM factinternetsales", conn)

# Merge dataframes
merged_df = pd.merge(product_categories_df, internet_sales_df, on="productcategorykey")

# Calculate total sales per product category
sales_per_category = merged_df.groupby("englishproductcategoryname")["salesamount"].sum().reset_index()

# Create a bar chart
fig, ax = plt.subplots(figsize=(10, 6))
sales_per_category.plot(x="englishproductcategoryname", y="salesamount", kind="bar", ax=ax, color="skyblue")
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Pendapatan Penjualan")
ax.set_title("Pendapatan Penjualan per Kategori Produk")
ax.set_xticklabels(sales_per_category["englishproductcategoryname"], rotation=45, ha="right")

# Streamlit App
st.title("Pendapatan Penjualan per Kategori Produk")

# Display the chart in Streamlit
st.pyplot(fig)

# Additional Streamlit Features (Optional)
# You can add more features to your Streamlit app, such as:
# - Filters to select specific product categories
# - Interactive charts that allow users to hover over data points
# - Text explanations or descriptions of the data
