import streamlit as st
from config.modules.miembrogapc import miembros_views

def cargar():
    st.header("Gestión de Miembros")

    submenu = st.selectbox(
        "Selecciona una opción:",
        ["Agregar miembro", "Ver miembro", "Ver todos los miembros"]
    )

    if submenu == "Agregar miembro":
        miembros_views.form_agregar()

    elif submenu == "Ver miembro":
        miembros_views.ver_miembro()

    elif submenu == "Ver todos los miembros":
        miembros_views.lista_miembros()
