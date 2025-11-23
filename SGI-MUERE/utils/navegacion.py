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
    info_grupo  # Cambiado de configuracion a info_grupo
)

def mostrar_modulo():
    """Muestra el módulo actual seleccionado"""
    modulo = st.session_state.modulo_actual
    
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
    elif modulo == 'configuracion':  # Mantener compatibilidad con el botón viejo
        info_grupo.mostrar_modulo_info_grupo()
    else:
        dashboard.mostrar_dashboard_principal()
