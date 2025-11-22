import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def mostrar_modulo_miembros():
    """Muestra el módulo de gestión de miembros"""
    
    usuario = st.session_state.usuario
    id_grupo = usuario.get('id_grupo', 1)
    
    # Header del módulo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header">👥 Gestión de Miembros</div>', unsafe_allow_html=True)
    
    # Botón para volver al dashboard
    if st.button("← Volver al Dashboard", use_container_width=False):
        st.session_state.current_module = None
        st.rerun()
    
    st.markdown("---")
    
    # Obtener miembros reales de la base de datos
    def obtener_miembros_grupo(id_grupo):
        try:
            conexion = obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT m.id_miembro, m.nombre, m.telefono, m.dui, m.correo, r.tipo_rol
                    FROM miembrogapc m
                    JOIN rol r ON m.id_rol = r.id_rol
                    WHERE m.id_grupo = %s
                    ORDER BY m.nombre
                """, (id_grupo,))
                miembros = cursor.fetchall()
                cursor.close()
                conexion.close()
                return miembros
        except Exception as e:
            st.error(f"Error al obtener miembros: {e}")
        return []
    
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Miembros", "➕ Agregar Miembro", "📊 Estadísticas"])
    
    with tab1:
        st.subheader("Lista de Miembros del Grupo")
        miembros = obtener_miembros_grupo(id_grupo)
        
        if miembros:
            df_miembros = pd.DataFrame(miembros)
            st.dataframe(
                df_miembros,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id_miembro": "ID",
                    "nombre": "Nombre",
                    "telefono": "Teléfono", 
                    "dui": "DUI",
                    "correo": "Correo",
                    "tipo_rol": "Rol"
                }
            )
        else:
            st.warning("No se encontraron miembros en este grupo")
    
    with tab2:
        st.subheader("Agregar Nuevo Miembro")
        st.info("🔧 Formulario para agregar miembros - En desarrollo")
    
    with tab3:
        st.subheader("Estadísticas de Miembros")
        st.info("🔧 Estadísticas de miembros - En desarrollo")
