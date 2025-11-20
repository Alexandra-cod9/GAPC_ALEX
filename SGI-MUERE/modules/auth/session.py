import streamlit as st

def verificar_autenticacion():
    """Verifica si el usuario está autenticado"""
    if 'usuario' not in st.session_state or not st.session_state.usuario:
        st.warning("🔐 Debes iniciar sesión para acceder a esta página")
        return False
    return True

def cerrar_sesion():
    """Cierra la sesión del usuario"""
    st.session_state.usuario = None
    st.success("Sesión cerrada exitosamente")
    st.rerun()

def obtener_usuario_actual():
    """Obtiene la información del usuario actual"""
    return st.session_state.usuario if 'usuario' in st.session_state else None