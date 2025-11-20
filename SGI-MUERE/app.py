import streamlit as st
from modules.auth.login import mostrar_formulario_login
from modules.auth.session import verificar_autenticacion, cerrar_sesion
from modules.dashboard.main import mostrar_dashboard_principal
from utils.helpers import inicializar_session_state

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
inicializar_session_state()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        color: #6f42c1;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton button {
        background-color: #6f42c1;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    
    # Sidebar para navegación
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/6f42c1/white?text=Sistema+GAPC", width=150)
        st.markdown("---")
        
        if st.session_state.usuario:
            st.write(f"👤 **{st.session_state.usuario['nombre']}**")
            st.write(f"🎭 Rol: {st.session_state.usuario.get('tipo_rol', 'Usuario')}")
            
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                cerrar_sesion()
    
    # Contenido principal
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        mostrar_dashboard_principal()

if __name__ == "__main__":
    main()import streamlit as st
from modules.auth.login import mostrar_formulario_login
from modules.auth.session import verificar_autenticacion, cerrar_sesion
from modules.dashboard.main import mostrar_dashboard_principal
from utils.helpers import inicializar_session_state

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
inicializar_session_state()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        color: #6f42c1;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton button {
        background-color: #6f42c1;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    
    # Sidebar para navegación
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/6f42c1/white?text=Sistema+GAPC", width=150)
        st.markdown("---")
        
        if st.session_state.usuario:
            st.write(f"👤 **{st.session_state.usuario['nombre']}**")
            st.write(f"🎭 Rol: {st.session_state.usuario.get('tipo_rol', 'Usuario')}")
            
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                cerrar_sesion()
    
    # Contenido principal
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        mostrar_dashboard_principal()

if __name__ == "__main__":
    main()
