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
    elif modulo == 'configuracion':
        configuracion.mostrar_modulo_configuracion()
    else:
        dashboard.mostrar_dashboard_principal()
        import streamlit as st

def mostrar_modulo():
    """Muestra el módulo actual seleccionado"""
    modulo = st.session_state.modulo_actual
    
    try:
        # Contenido específico de cada módulo
        if modulo == 'dashboard':
            from modules.dashboard import mostrar_dashboard_principal
            mostrar_dashboard_principal()
        elif modulo == 'miembros':
            from modules.miembros import mostrar_modulo_miembros
            mostrar_modulo_miembros()
        elif modulo == 'reuniones':
            from modules.reuniones import mostrar_modulo_reuniones
            mostrar_modulo_reuniones()
        elif modulo == 'aportes':
            from modules.aportes import mostrar_modulo_aportes
            mostrar_modulo_aportes()
        elif modulo == 'prestamos':
            from modules.prestamos import mostrar_modulo_prestamos
            mostrar_modulo_prestamos()
        elif modulo == 'multas':
            from modules.multas import mostrar_modulo_multas
            mostrar_modulo_multas()
        elif modulo == 'reportes':
            from modules.reportes import mostrar_modulo_reportes
            mostrar_modulo_reportes()
        elif modulo == 'cierre':
            from modules.cierre import mostrar_modulo_cierre
            mostrar_modulo_cierre()
        elif modulo == 'configuracion':
            from modules.configuracion import mostrar_modulo_configuracion
            mostrar_modulo_configuracion()
        else:
            from modules.dashboard import mostrar_dashboard_principal
            mostrar_dashboard_principal()
    except ImportError as e:
        st.error(f"Error al cargar módulo: {e}")
        st.info("Algunos módulos pueden estar en desarrollo")
        from modules.dashboard import mostrar_dashboard_principal
        mostrar_dashboard_principal()
