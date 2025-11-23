import streamlit as st

def menu():
    st.sidebar.markdown(
        "<h2 style='color:#4b0082; font-weight:700;'>Menú GAPT</h2>",
        unsafe_allow_html=True
    )

    seleccion = st.sidebar.radio(
        "Navegación",
        [
            "Dashboard",
            "Miembros",
            "Reuniones",
            "Aportes",
            "Préstamos",
            "Multas",
            "Reportes",
            "Cierres",
            "Configuración"
        ]
    )

    return seleccion
