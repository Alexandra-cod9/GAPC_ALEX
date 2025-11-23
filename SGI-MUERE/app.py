# app.py - ARCHIVO PRINCIPAL SIMPLIFICADO
import streamlit as st

# Importar módulos
from modules.dashboard import mostrar_dashboard_principal
from modules.miembros.miembros import mostrar_modulo_miembros
from config.conexion import obtener_conexion

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado (mantén tu CSS actual)
st.markdown("""
<style>
    /* MANTÉN TODO TU CSS ACTUAL AQUÍ */
    .main-header { color: #6f42c1; text-align: center; margin-bottom: 0.5rem; font-size: 1.5rem; }
    /* ... resto de tu CSS */
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'id_grupo' not in st.session_state:
    st.session_state.id_grupo = None
if 'modulo_actual' not in st.session_state:
    st.session_state.modulo_actual = 'dashboard'

# FUNCIONES BÁSICAS (login) - mantén tus funciones actuales de login
def verificar_login_real(correo, contrasena):
    # ... (tu código actual de login)
    pass

def mostrar_formulario_login():
    # ... (tu código actual de login)
    pass

# FUNCIÓN PARA MOSTRAR MÓDULOS
def mostrar_modulo():
    """Muestra el módulo actual seleccionado"""
    modulo = st.session_state.modulo_actual
    
    if modulo == 'dashboard':
        mostrar_dashboard_principal()
    elif modulo == 'miembros':
        mostrar_modulo_miembros()
    elif modulo == 'reuniones':
        st.info("Módulo de reuniones - En desarrollo")
        if st.button("⬅️ Volver al Dashboard"):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    # ... agregar otros módulos según los vayas creando

# APLICACIÓN PRINCIPAL
def main():
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        mostrar_modulo()

if __name__ == "__main__":
    main()
