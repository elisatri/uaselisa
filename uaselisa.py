import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pymysql

# Function to establish MySQL connection
def get_mysql_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="dump-dw_aw",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to fetch data from MySQL
def fetch_data(conn):
    query = """
        SELECT pc.productcategorykey, pc.englishproductcategoryname, SUM(fs.salesamount) AS total_sales 
        FROM dimproductcategory pc 
        INNER JOIN factinternetsales fs ON pc.productcategorykey = fs.productcategorykey 
        GROUP BY pc.productcategorykey, pc.englishproductcategoryname 
        ORDER BY total_sales DESC
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data)
            return df
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        return pd.DataFrame()

# Main Streamlit application
def main():
    # Connect to MySQL
    conn = get_mysql_connection()

    # Check if connection is successful
    if conn:
        try:
            # Fetch data
            df = fetch_data(conn)

            # Close connection
            conn.close()

            # Prepare data for plotting
            if not df.empty:
                # Create bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                df.plot(x="englishproductcategoryname", y="total_sales", kind="bar", ax=ax, color="skyblue")
                ax.set_xlabel("Product Category")
                ax.set_ylabel("Sales Revenue")
                ax.set_title("Sales Revenue per Product Category")
                ax.set_xticklabels(df["englishproductcategoryname"], rotation=45, ha="right")
                
                # Display chart in Streamlit
                st.title("Sales Revenue per Product Category")
                st.pyplot(fig)
            else:
                st.warning("No data available.")
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Failed to connect to MySQL. Check connection parameters.")

# Run the app
if __name__ == "__main__":
    main()
