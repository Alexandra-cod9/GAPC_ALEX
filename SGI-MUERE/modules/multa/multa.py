import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def mostrar_modulo_multas():
    """Muestra el módulo de gestión de multas"""
    
    usuario = st.session_state.usuario
    
    # Header del módulo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header">⚠️ Gestión de Multas</div>', unsafe_allow_html=True)
    
    # Botón para volver al dashboard
    if st.button("← Volver al Dashboard", use_container_width=False):
        st.session_state.current_module = None
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("Registro de Multas")
    st.info("🔧 Control de multas y sanciones - En desarrollo")
