import streamlit as st
from config.conexion import obtener_conexion
from database.queries import QUERIES_DASHBOARD
from utils.helpers import mostrar_estado_badge, formatear_fecha

def mostrar_dashboard_principal():
    """Muestra el dashboard principal del sistema"""
    
    usuario = st.session_state.usuario
    st.title(f"🏠 Dashboard - Bienvenido/a {usuario['nombre']}")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Miembros Activos", "25", "+3")
    
    with col2:
        st.metric("Préstamos Activos", "8", "-1")
    
    with col3:
        st.metric("Reuniones Este Mes", "4", "+2")
    
    # Sección de reuniones recientes
    st.subheader("📅 Reuniones Recientes")
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(QUERIES_DASHBOARD['reuniones_recientes'], (usuario.get('id_grupo', 1),))
            reuniones = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            for reunion in reuniones:
                with st.expander(f"Reunión del {formatear_fecha(reunion['fecha'])}"):
                    st.write(reunion['acuerdos'] or "Sin acuerdos registrados")
    except Exception as e:
        st.error(f"Error al cargar reuniones: {e}")
    
    # Acciones rápidas
    st.subheader("🚀 Acciones Rápidas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Registrar Asistencia", use_container_width=True):
            st.switch_page("pages/reuniones.py")
    
    with col2:
        if st.button("💰 Registrar Aporte", use_container_width=True):
            st.switch_page("pages/aportes.py")
    
    with col3:
        if st.button("📊 Ver Reportes", use_container_width=True):
            st.switch_page("pages/reportes.py")
            