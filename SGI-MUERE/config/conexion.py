import pymysql
import streamlit as st

def obtener_conexion():
    try:
        conexion = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='1234',
            database='sgi_gapc',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conexion
    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
        return None