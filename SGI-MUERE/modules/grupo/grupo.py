import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def mostrar_modulo_grupo():
    """Muestra el módulo de gestión del grupo"""
    
    usuario = st.session_state.usuario
    
    # Header del módulo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header">🏢 Gestión del Grupo</div>', unsafe_allow_html=True)
    
    # Botón para volver al dashboard
    if st.button("← Volver al Dashboard", use_container_width=False):
        st.session_state.current_module = None
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("Información del Grupo")
    st.info("🔧 Configuración del grupo - En desarrollo")
