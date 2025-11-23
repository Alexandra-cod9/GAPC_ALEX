# modules/miembros/miembros.py
import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def mostrar_modulo_miembros():
    """Módulo de gestión de miembros"""
    
    st.markdown("# 👥 Gestión de Miembros")
    
    # Botón para volver al dashboard
    if st.button("⬅️ Volver al Dashboard"):
        st.session_state.modulo_actual = 'dashboard'
        st.rerun()
    
    st.markdown("---")
    
    # Pestañas para organizar las funciones
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Miembros", "➕ Nuevo Miembro", "✏️ Editar Miembro", "📊 Estadísticas"])
    
    with tab1:
        mostrar_lista_miembros()
    
    with tab2:
        mostrar_formulario_nuevo_miembro()
    
    with tab3:
        mostrar_edicion_miembro()
    
    with tab4:
        mostrar_estadisticas_miembros()

def mostrar_lista_miembros():
    """Muestra la lista de miembros"""
    st.subheader("Lista de Miembros")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener miembros del grupo actual
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
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
            
            if miembros:
                df = pd.DataFrame(miembros)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay miembros registrados en este grupo.")
                
    except Exception as e:
        st.error(f"Error al cargar miembros: {e}")

def mostrar_formulario_nuevo_miembro():
    """Muestra formulario para nuevo miembro"""
    st.subheader("Agregar Nuevo Miembro")
    
    with st.form("nuevo_miembro"):
        nombre = st.text_input("Nombre completo")
        telefono = st.text_input("Teléfono")
        dui = st.text_input("DUI")
        correo = st.text_input("Correo electrónico")
        contrasena = st.text_input("Contraseña", type="password")
        
        # Obtener roles disponibles
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_rol, tipo_rol FROM rol")
        roles = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        rol_options = {rol['tipo_rol']: rol['id_rol'] for rol in roles}
        rol_seleccionado = st.selectbox("Rol", options=list(rol_options.keys()))
        
        if st.form_submit_button("💾 Guardar Miembro"):
            if nombre and telefono and dui:
                # Aquí iría el código para guardar en la BD
                st.success(f"Miembro {nombre} guardado exitosamente!")
            else:
                st.warning("Por favor complete todos los campos obligatorios")

def mostrar_edicion_miembro():
    """Muestra interfaz para editar miembros"""
    st.subheader("Editar Miembro")
    st.info("Selecciona un miembro para editar sus datos")
    # Aquí irá el código para editar

def mostrar_estadisticas_miembros():
    """Muestra estadísticas de miembros"""
    st.subheader("Estadísticas de Miembros")
    st.info("Gráficas y estadísticas de miembros")
    # Aquí irán las gráficas
