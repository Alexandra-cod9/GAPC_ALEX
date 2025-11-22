import streamlit as st
from datetime import datetime

def formatear_fecha(fecha):
    """Formatea fecha para mostrar en la interfaz"""
    if isinstance(fecha, str):
        return fecha
    return fecha.strftime('%d/%m/%Y')

def mostrar_estado_badge(estado):
    """Muestra un badge de estado con colores"""
    colores = {
        'activo': '🟢',
        'pagado': '🔵', 
        'mora': '🔴',
        'presente': '✅',
        'ausente': '❌'
    }
    return colores.get(estado, '⚪')

def inicializar_session_state():
    """Inicializa variables de session_state si no existen"""
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None
    if 'id_grupo' not in st.session_state:
        st.session_state.id_grupo = None