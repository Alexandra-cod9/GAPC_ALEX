import streamlit as st

def mostrar_modulo_reportes():
    """Módulo de reportes y estadísticas"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 📊 Módulo de Reportes")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("Reportes y Estadísticas")
    st.info("🛠️ Módulo de Reportes - En desarrollo")