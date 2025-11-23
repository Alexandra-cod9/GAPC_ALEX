import streamlit as st
import sys
import os

# Agregar el directorio raíz al path para importaciones absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importaciones absolutas
from modules.dashboard import mostrar_dashboard_principal
from modules.miembros import mostrar_modulo_miembros
from modules.reuniones import mostrar_modulo_reuniones
from modules.aportes import mostrar_modulo_aportes
from modules.prestamos import mostrar_modulo_prestamos
from modules.multas import mostrar_modulo_multas
from modules.reportes import mostrar_modulo_reportes
from modules.cierre import mostrar_modulo_cierre
from modules.configuracion import mostrar_modulo_configuracion

def mostrar_modulo():
    """Muestra el módulo actual seleccionado"""
    modulo = st.session_state.modulo_actual
    
    st.write(f"🔍 DEBUG: Módulo actual = {modulo}")  # Línea de debug temporal
    
    # Contenido específico de cada módulo
    if modulo == 'dashboard':
        mostrar_dashboard_principal()
    elif modulo == 'miembros':
        mostrar_modulo_miembros()
    elif modulo == 'reuniones':
        mostrar_modulo_reuniones()
    elif modulo == 'aportes':
        mostrar_modulo_aportes()
    elif modulo == 'prestamos':
        mostrar_modulo_prestamos()
    elif modulo == 'multas':
        mostrar_modulo_multas()
    elif modulo == 'reportes':
        mostrar_modulo_reportes()
    elif modulo == 'cierre':
        mostrar_modulo_cierre()
    elif modulo == 'configuracion':
        mostrar_modulo_configuracion()
    else:
        mostrar_dashboard_principal()
