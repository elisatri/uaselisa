import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Define the file path
csv_file = "dump-dw_aw.csv"

# Load data from CSV
try:
    df = pd.read_csv(csv_file)

    # Calculate total sales per product category
    sales_per_category = df.groupby("englishproductcategoryname")["salesamount"].sum().reset_index()

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

except FileNotFoundError:
    st.error(f"File '{csv_file}' not found. Please make sure the file exists and the path is correct.")
except Exception as e:
    st.error(f"An error occurred: {e}")

# Additional Streamlit Features (Optional)
# You can add more features to your Streamlit app, such as:
# - Filters to select specific product categories
# - Interactive charts that allow users to hover over data points
# - Text explanations or descriptions of the data
