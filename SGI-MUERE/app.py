import streamlit as st
from modules.auth.login import verificar_login_real
from modules.dashboard.main import mostrar_dashboard_principal
from modules.miembros.miembro import mostrar_modulo_miembros
from config.conexion import obtener_conexion

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS (puedes moverlo a un archivo aparte)
st.markdown("""
<style>
    .main-header { color: #6f42c1; text-align: center; margin-bottom: 0.5rem; font-size: 1.5rem; }
    .stButton button { background-color: #6f42c1; color: white; border: none; padding: 0.3rem 0.6rem; border-radius: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'id_grupo' not in st.session_state:
    st.session_state.id_grupo = None
if 'current_module' not in st.session_state:
    st.session_state.current_module = None

# Función de login (mínima)
def mostrar_formulario_login():
    """Muestra el formulario de login"""
    # ... código reducido del login
    
# APLICACIÓN PRINCIPAL
def main():
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        if st.session_state.current_module == "miembros":
            mostrar_modulo_miembros()
        else:
            mostrar_dashboard_principal()

if __name__ == "__main__":
    main()
