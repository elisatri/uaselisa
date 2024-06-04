import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import mysql.connector

# Function to establish MySQL connection
def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='dump-dw_aw'
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to fetch data from MySQL
def fetch_data(conn):
    query = """
        SELECT pc.productkey, pc.englishproductname, SUM(fs.salesamount) AS total_sales FROM dimproduct pc 
        INNER JOIN factinternetsales fs ON pc.productkey = fs.productkey GROUP BY pc.productkey, pc.englishproductname ORDER BY total_sales DESC
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

# Main Streamlit application
def main():
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
            ax.set_title("Sales Revenue per Product")
            ax.set_xticklabels(df["englishproductname"], rotation=45, ha="right")
            
            # Display chart in Streamlit
            st.title("Sales Revenue per Product Category")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Failed to connect to MySQL. Check connection parameters.")

# Run the app
if __name__ == "__main__":
    main()
