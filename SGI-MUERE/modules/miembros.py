import streamlit as st

def mostrar_modulo_miembros():
    """Módulo de gestión de miembros"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 👥 Módulo de Miembros")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("Gestión de Miembros")
    
    # Aquí irá todo el código del módulo de miembros
    st.info("🛠️ Módulo de Miembros - En desarrollo")
    
    # Ejemplo de opciones básicas
    opcion = st.selectbox(
        "Selecciona una acción:",
        ["Ver lista de miembros", "Agregar nuevo miembro", "Editar miembro", "Eliminar miembro"]
    )
    
    if opcion == "Ver lista de miembros":
        st.write("Aquí se mostrará la lista de miembros...")
    elif opcion == "Agregar nuevo miembro":
        st.write("Formulario para agregar nuevo miembro...")