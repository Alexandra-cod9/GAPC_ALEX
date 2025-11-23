import streamlit as st

# Simulación de usuarios
USERS = {
    "admin": {"password": "1234", "grupo_id": 1},
    "alex": {"password": "gapt2025", "grupo_id": 2}
}

def login():
    # Título principal
    st.markdown("<h1 style='text-align: center;'>GAPT - Inicio de Sesión</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:16px;'>Bienvenido, ingresa tus credenciales.</p>", unsafe_allow_html=True)
    
    # Espaciado
    st.write("")

    # Campo Usuario
    user = st.text_input("Usuario")

    # Campo Contraseña
    password = st.text_input("Contraseña", type="password")

    # Botón de ingreso
    if st.button("Ingresar"):
        if user in USERS and USERS[user]["password"] == password:
            # Guardar sesión
            st.session_state["logged"] = True
            st.session_state["user"] = user
            st.session_state["grupo_id"] = USERS[user]["grupo_id"]

            st.success(f"Bienvenido {user.capitalize()} 👋")
        else:
            st.error("Usuario o contraseña incorrectos.")
