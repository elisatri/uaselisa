import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Read SQL data from file
with open("dump-dw_aw-202403050806.sql", "r") as f:
    sql_data = f.read()

# Execute SQL queries using pandas-sql
import pandas_sql
engine = pandas_sql.make_engine("sqlite:///:memory:")
engine.execute(sql_data)

# Fetch data into DataFrames
product_categories_df = pd.read_sql_table("dimproductcategory", engine)
internet_sales_df = pd.read_sql_table("factinternetsales", engine)

# Merge dataframes
merged_df = product_categories_df.merge(internet_sales_df, on="productcategorykey")

# Calculate total sales per product category
sales_per_category = merged_df.groupby("englishproductcategoryname")["salesamount"].sum()

# Create a bar chart
fig, ax = plt.subplots(figsize=(10, 6))
sales_per_category.plot(kind="bar", ax=ax, color="skyblue")
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Pendapatan Penjualan")
ax.set_title("Pendapatan Penjualan per Kategori Produk")
ax.set_xticks(rotation=45, ha="right")

# Streamlit App
st.title("Pendapatan Penjualan per Kategori Produk")

# Display the chart in Streamlit
st.pyplot(fig)

# Additional Streamlit Features (Optional)
# You can add more features to your Streamlit app, such as:
# - Filters to select specific product categories
# - Interactive charts that allow users to hover over data points
# - Text explanations or descriptions of the data
