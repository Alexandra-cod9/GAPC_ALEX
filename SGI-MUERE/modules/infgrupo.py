import streamlit as st

def mostrar_modulo_informacion_de_grupo():
    """Módulo de informacion de grupo"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# informacion de grupo")
    with col2:
        if st.button("⬅️ Volver al inicio", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("informacion de grupo")
    st.info("🛠️ Módulo de Configuración - En desarrollo")
