import streamlit as st

def mostrar_modulo_configuracion():
    """Módulo de configuración"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# ⚙️ Módulo de Configuración")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("Configuración del Sistema")
    st.info("🛠️ Módulo de Configuración - En desarrollo")
    