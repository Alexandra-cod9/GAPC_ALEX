import streamlit as st
import pandas as pd
from datetime import datetime

def obtener_conexion():
    """Función de conexión a la base de datos"""
    try:
        import pymysql
        conexion = pymysql.connect(
            host='bhzcn4gxgbe5tcxihqd1-mysql.services.clever-cloud.com',
            user='usv5pnvafxbrw5hs',
            password='WiOSztB38WxsKuXjnQgT',
            database='bhzcn4gxgbe5tcxihqd1',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        return conexion
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

def mostrar_modulo_miembros():
    """Módulo de gestión de miembros"""
    
    st.title("👥 Gestión de Miembros")
    
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Miembros", "➕ Agregar Miembro", "📊 Estadísticas"])
    
    with tab1:
        mostrar_lista_miembros()
    
    with tab2:
        mostrar_formulario_agregar_miembro()
    
    with tab3:
        mostrar_estadisticas_miembros()

def mostrar_lista_miembros():
    """Muestra la lista de miembros del grupo"""
    
    st.subheader("📋 Miembros del Grupo")
    
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
                # Convertir a DataFrame para mejor visualización
                df = pd.DataFrame(miembros)
                st.dataframe(
                    df,
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
                
                # Mostrar resumen
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Miembros", len(miembros))
                with col2:
                    roles_count = df['tipo_rol'].value_counts()
                    st.metric("Roles Diferentes", len(roles_count))
                with col3:
                    st.metric("Miembros con Email", df['correo'].notna().sum())
                    
            else:
                st.info("📝 No hay miembros registrados en este grupo aún.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar miembros: {e}")

def mostrar_formulario_agregar_miembro():
    """Muestra formulario para agregar nuevo miembro"""
    
    st.subheader("➕ Agregar Nuevo Miembro")
    
    with st.form("form_agregar_miembro"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre Completo *", placeholder="Ej: María González")
            telefono = st.text_input("Teléfono *", placeholder="Ej: 7777-8888")
            dui = st.text_input("DUI *", placeholder="Ej: 12345678-9")
            
        with col2:
            correo = st.text_input("Correo Electrónico", placeholder="Ej: usuario@email.com")
            
            # Obtener roles disponibles
            try:
                conexion = obtener_conexion()
                if conexion:
                    cursor = conexion.cursor()
                    cursor.execute("SELECT id_rol, tipo_rol FROM rol")
                    roles = cursor.fetchall()
                    cursor.close()
                    conexion.close()
                    
                    roles_dict = {rol['tipo_rol']: rol['id_rol'] for rol in roles}
                    rol_seleccionado = st.selectbox("Rol *", list(roles_dict.keys()))
                    
            except Exception as e:
                st.error(f"Error al cargar roles: {e}")
                rol_seleccionado = "socio"
        
        # Información adicional
        st.markdown("**Nota:** El miembro se agregará al grupo actual")
        
        submitted = st.form_submit_button("💾 Guardar Miembro", use_container_width=True)
        
        if submitted:
            if nombre and telefono and dui:
                try:
                    conexion = obtener_conexion()
                    if conexion:
                        cursor = conexion.cursor()
                        
                        # Insertar nuevo miembro
                        cursor.execute("""
                            INSERT INTO miembrogapc 
                            (nombre, telefono, dui, id_grupo, id_rol, correo, contrasena)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            nombre.strip(),
                            telefono.strip(),
                            dui.strip(),
                            st.session_state.usuario.get('id_grupo', 1),
                            roles_dict[rol_seleccionado],
                            correo.strip() if correo else None,
                            "temp123"  # Contraseña temporal
                        ))
                        
                        conexion.commit()
                        cursor.close()
                        conexion.close()
                        
                        st.success(f"✅ Miembro {nombre} agregado exitosamente!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error al guardar miembro: {e}")
            else:
                st.warning("⚠️ Por favor complete los campos obligatorios (*)")

def mostrar_estadisticas_miembros():
    """Muestra estadísticas de miembros"""
    
    st.subheader("📊 Estadísticas de Miembros")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Estadísticas básicas
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT id_rol) as roles_diferentes,
                    COUNT(correo) as con_correo
                FROM miembrogapc 
                WHERE id_grupo = %s
            """, (id_grupo,))
            stats = cursor.fetchone()
            
            # Distribución por roles
            cursor.execute("""
                SELECT r.tipo_rol, COUNT(*) as cantidad
                FROM miembrogapc m
                JOIN rol r ON m.id_rol = r.id_rol
                WHERE m.id_grupo = %s
                GROUP BY r.tipo_rol
                ORDER BY cantidad DESC
            """, (id_grupo,))
            roles_dist = cursor.fetchall()
            
            cursor.close()
            conexion.close()
            
            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Miembros", stats['total'])
            with col2:
                st.metric("Roles Diferentes", stats['roles_diferentes'])
            with col3:
                st.metric("Con Correo", stats['con_correo'])
            
            # Mostrar distribución de roles
            if roles_dist:
                st.subheader("📈 Distribución por Roles")
                roles_df = pd.DataFrame(roles_dist)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.bar_chart(roles_df.set_index('tipo_rol')['cantidad'])
                
                with col2:
                    for rol in roles_dist:
                        st.write(f"**{rol['tipo_rol']}:** {rol['cantidad']}")
            
    except Exception as e:
        st.error(f"❌ Error al cargar estadísticas: {e}")

# Función principal del módulo
def main():
    if not st.session_state.usuario:
        st.warning("🔐 Debes iniciar sesión para acceder a este módulo")
        return
    
    # Botón para volver al dashboard
    if st.button("← Volver al Dashboard"):
        st.session_state.pagina_actual = "dashboard"
        st.rerun()
    
    mostrar_modulo_miembros()

if __name__ == "__main__":
    main()
