import streamlit as st
from modules import (
    dashboard, 
    miembros, 
    reuniones, 
    aportes,
    prestamos, 
    multas, 
    reportes, 
    cierre, 
    configuracion
)

def mostrar_modulo():
    """Muestra el módulo actual seleccionado"""
    modulo = st.session_state.get('modulo_actual', 'dashboard')
    
    # Contenido específico de cada módulo
    if modulo == 'dashboard':
        dashboard.mostrar_dashboard_principal()
    elif modulo == 'miembros':
        miembros.mostrar_modulo_miembros()
    elif modulo == 'reuniones':
        reuniones.mostrar_modulo_reuniones()
    elif modulo == 'aportes':
        aportes.mostrar_modulo_aportes()
    elif modulo == 'prestamos':
        prestamos.mostrar_modulo_prestamos()
    elif modulo == 'multas':
        multas.mostrar_modulo_multas()
    elif modulo == 'reportes':
        reportes.mostrar_modulo_reportes()
    elif modulo == 'cierre':
        cierre.mostrar_modulo_cierre()
    elif modulo == 'configuracion':
        configuracion.mostrar_modulo_configuracion()
    else:
        # Fallback al dashboard si el módulo no existe
        dashboard.mostrar_dashboard_principal()

def inicializar_session_state():
    """Inicializa las variables de session_state si no existen"""
    if 'modulo_actual' not in st.session_state:
        st.session_state.modulo_actual = 'dashboard'
    if 'usuario' not in st.session_state:
        st.session_state.usuario = {
            'id_grupo': 1,
            'nombre': 'Usuario Demo',
            'rol': 'Administrador'
        }

def main():
    """Función principal de la aplicación"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Sistema GAPC",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicializar session state
    inicializar_session_state()
    
    # Mostrar el módulo actual
    mostrar_modulo()

if __name__ == "__main__":
    main()
