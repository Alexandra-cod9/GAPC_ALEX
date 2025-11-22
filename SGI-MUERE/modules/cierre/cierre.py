import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def mostrar_modulo_cierre():
    """Muestra el módulo de cierre de período"""
    
    usuario = st.session_state.usuario
    
    # Header del módulo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header">🔄 Cierre de Período</div>', unsafe_allow_html=True)
    
    # Botón para volver al dashboard
    if st.button("← Volver al Dashboard", use_container_width=False):
        st.session_state.current_module = None
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("Cierre Contable")
    st.info("🔧 Cierre mensual/anual - En desarrollo")
