import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Function to establish MySQL connection
def get_mysql_connection():
    try:
        # Adjust the connection string as needed
        engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/dump-dw_aw')
        conn = engine.connect()
        print("Connection to MySQL database successful")
        return conn
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to fetch data from MySQL
def fetch_data(conn):
    query = """
        SELECT pc.productkey, pc.englishproductname, SUM(fs.salesamount) AS total_sales
        FROM dimproduct pc
        INNER JOIN factinternetsales fs ON pc.productkey = fs.productkey
        GROUP BY pc.productkey, pc.englishproductname
        ORDER BY total_sales DESC
        LIMIT 25
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        return pd.DataFrame()

# Connect to MySQL
conn = get_mysql_connection()

# Check if connection is successful
if conn:
    try:
        # Fetch data
        data = fetch_data(conn)

        # Close connection
        conn.close()

        # Prepare data for plotting
        df = pd.DataFrame(data, columns=['productkey', 'englishproductname', 'total_sales'])

        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        df.plot(x="englishproductname", y="total_sales", kind="bar", ax=ax, color="skyblue")
        ax.set_xlabel("Product")
        ax.set_ylabel("Sales Revenue")
        ax.set_title("Sales Revenue per Product (COMPARISON)")
        ax.set_xticklabels(df["englishproductname"], rotation=45, ha="right")

        # Show plot
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error: {e}")
else:
    print("Failed to connect to MySQL. Check connection parameters.")
