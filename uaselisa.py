import mysql.connector
import streamlit as st

def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="dump-dw_aw"
        )
        print("Connection to MySQL database successful")
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Testing the function
conn = get_mysql_connection()
