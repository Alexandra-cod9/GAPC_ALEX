import streamlit as st
import bcrypt
from config.conexion import obtener_conexion
from database.queries import QUERIES_AUTH

def verificar_login(correo, contrasena):
    """Verifica las credenciales del usuario"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(QUERIES_AUTH['login'], (correo,))
            usuario = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if usuario and bcrypt.checkpw(contrasena.encode('utf-8'), usuario['contrasena'].encode('utf-8')):
                return usuario
        return None
    except Exception as e:
        st.error(f"Error en login: {e}")
        return None

def mostrar_formulario_login():
    """Muestra el formulario de login en Streamlit"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.header("🔐 Iniciar Sesión - Sistema GAPC")
        
        with st.form("login_form"):
            correo = st.text_input("📧 Correo Electrónico")
            contrasena = st.text_input("🔒 Contraseña", type="password")
            
            if st.form_submit_button("🚀 Ingresar", use_container_width=True):
                if correo and contrasena:
                    usuario = verificar_login(correo, contrasena)
                    if usuario:
                        st.session_state.usuario = usuario
                        st.success(f"¡Bienvenido/a {usuario['nombre']}!")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")
                else:
                    st.warning("Por favor complete todos los campos")