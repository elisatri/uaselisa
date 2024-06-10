import streamlit as st
import mysql.connector

# Function to establish MySQL connection
def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="dump-dw_aw"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Streamlit app
st.title("MySQL Database Connection Status")

# Connect to MySQL
conn = get_mysql_connection()

# Check if connection is successful
if conn:
    st.success("Connection to MySQL database successful")
    conn.close()  # Close the connection if it's successful
else:
    st.error("Failed to connect to MySQL. Check connection parameters.")
