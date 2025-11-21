import streamlit as st
import pandas as pd
from datetime import datetime

def mostrar_modulo_miembros():
    st.markdown("## 👥 Gestión de Miembros")
    
    # Verificar autenticación
    if 'usuario' not in st.session_state or not st.session_state.usuario:
        st.warning("🔐 Debes iniciar sesión para acceder a este módulo")
        return
    
    usuario = st.session_state.usuario
    id_grupo = usuario.get('id_grupo')
    
    # Conexión a BD
    def obtener_miembros_grupo(id_grupo):
        try:
            conexion = st.session_state.conexion
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
            return miembros
        except Exception as e:
            st.error(f"Error al cargar miembros: {e}")
            return []
    
    # Obtener roles disponibles
    def obtener_roles():
        try:
            conexion = st.session_state.conexion
            cursor = conexion.cursor()
            cursor.execute("SELECT id_rol, tipo_rol FROM rol")
            roles = cursor.fetchall()
            cursor.close()
            return {rol['tipo_rol']: rol['id_rol'] for rol in roles}
        except Exception as e:
            st.error(f"Error al cargar roles: {e}")
            return {}
    
    # Pestañas del módulo
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Miembros", "➕ Nuevo Miembro", "📊 Estadísticas"])
    
    with tab1:
        st.subheader("Miembros del Grupo")
        
        miembros = obtener_miembros_grupo(id_grupo)
        
        if miembros:
            # Convertir a DataFrame para mejor visualización
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
            
            # Métricas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Miembros", len(miembros))
            with col2:
                roles_count = df_miembros['tipo_rol'].value_counts()
                st.metric("Socios", roles_count.get('socio', 0))
            with col3:
                st.metric("Directiva", len(miembros) - roles_count.get('socio', 0))
                
        else:
            st.info("📝 No hay miembros registrados en este grupo")
    
    with tab2:
        st.subheader("Registrar Nuevo Miembro")
        
        with st.form("nuevo_miembro_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre Completo *", placeholder="Ej: María González")
                telefono = st.text_input("Teléfono *", placeholder="Ej: 7777-8888")
                dui = st.text_input("DUI *", placeholder="Ej: 12345678-9")
            
            with col2:
                correo = st.text_input("Correo Electrónico", placeholder="ejemplo@correo.com")
                contrasena = st.text_input("Contraseña", type="password", placeholder="Opcional")
                
                roles = obtener_roles()
                rol_seleccionado = st.selectbox(
                    "Rol *",
                    options=list(roles.keys()),
                    index=list(roles.keys()).index('socio') if 'socio' in roles else 0
                )
            
            submitted = st.form_submit_button("💾 Guardar Miembro", use_container_width=True)
            
            if submitted:
                if nombre and telefono and dui:
                    try:
                        conexion = st.session_state.conexion
                        cursor = conexion.cursor()
                        
                        cursor.execute("""
                            INSERT INTO miembrogapc 
                            (nombre, telefono, dui, correo, contrasena, id_grupo, id_rol)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            nombre.strip(),
                            telefono.strip(),
                            dui.strip(),
                            correo.strip() if correo else None,
                            contrasena if contrasena else None,
                            id_grupo,
                            roles[rol_seleccionado]
                        ))
                        
                        conexion.commit()
                        cursor.close()
                        st.success(f"✅ Miembro {nombre} registrado exitosamente!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al guardar miembro: {e}")
                else:
                    st.warning("⚠️ Completa los campos obligatorios (*)")
    
    with tab3:
        st.subheader("Estadísticas de Miembros")
        
        if miembros:
            df = pd.DataFrame(miembros)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribución por roles
                st.markdown("**📊 Distribución por Roles**")
                roles_dist = df['tipo_rol'].value_counts()
                st.bar_chart(roles_dist)
            
            with col2:
                # Métricas adicionales
                st.markdown("**📈 Información General**")
                st.metric("Miembros con correo", df['correo'].notna().sum())
                st.metric("Miembros con teléfono", df['telefono'].notna().sum())

if __name__ == "__main__":
    mostrar_modulo_miembros()