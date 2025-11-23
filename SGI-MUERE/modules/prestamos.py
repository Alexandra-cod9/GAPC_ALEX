import streamlit as st

def mostrar_modulo_prestamos():
    """Módulo de gestión de préstamos"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 💳 Módulo de Préstamos")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("Gestión de Préstamos")
    st.info("🛠️ Módulo de Préstamos - En desarrollo")
