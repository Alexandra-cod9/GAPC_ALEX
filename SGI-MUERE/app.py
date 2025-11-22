import streamlit as st
from config.modules_router import cargar_modulo

st.set_page_config(page_title="GAPC System", layout="wide")

st.title("Sistema GAPC")

menu_principal = [
    "Miembros",
    "Reuniones",
    "Aportes",
    "Préstamos",
    "Multas",
    "Cierre",
    "Reportes",
    "Configuraciones"
]

opcion = st.sidebar.radio("Menú principal", menu_principal)

cargar_modulo(opcion)
