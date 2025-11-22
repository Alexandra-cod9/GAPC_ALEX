# MÓDULO DE GESTIÓN DE MIEMBROS
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
        """Obtiene los miembros del grupo desde la base de datos"""
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
    
    # Obtener roles disponibles
    def obtener_roles():
        """Obtiene los roles disponibles"""
        try:
            conexion = obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT id_rol, tipo_rol FROM rol")
                roles = cursor.fetchall()
                cursor.close()
                conexion.close()
                return {rol['tipo_rol']: rol['id_rol'] for rol in roles}
        except Exception as e:
            st.error(f"Error al obtener roles: {e}")
        return {}
    
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Miembros", "➕ Agregar Miembro", "📊 Estadísticas"])
    
    with tab1:
        st.subheader("Lista de Miembros del Grupo")
        
        # Cargar miembros
        miembros = obtener_miembros_grupo(id_grupo)
        
        if miembros:
            # Mostrar en dataframe
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
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Miembros", len(miembros))
            with col2:
                roles_count = df_miembros['tipo_rol'].value_counts()
                st.metric("Socios", roles_count.get('socio', 0))
            with col3:
                st.metric("Directivos", len(df_miembros) - roles_count.get('socio', 0))
            with col4:
                st.metric("Con Email", df_miembros['correo'].notna().sum())
                
        else:
            st.warning("No se encontraron miembros en este grupo")
    
    with tab2:
        st.subheader("Agregar Nuevo Miembro")
        
        with st.form("form_agregar_miembro"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre Completo *", placeholder="Ej: María González")
                telefono = st.text_input("Teléfono *", placeholder="Ej: 7777-8888")
                dui = st.text_input("DUI *", placeholder="Ej: 123456789")
                
            with col2:
                correo = st.text_input("Correo Electrónico", placeholder="Ej: usuario@email.com")
                roles_dict = obtener_roles()
                rol_seleccionado = st.selectbox("Rol *", options=list(roles_dict.keys()))
                contrasena = st.text_input("Contraseña (opcional)", type="password", 
                                         placeholder="Solo para acceso al sistema")
            
            st.markdown("** * Campos obligatorios**")
            
            if st.form_submit_button("✅ Guardar Miembro", use_container_width=True):
                if nombre and telefono and dui and rol_seleccionado:
                    try:
                        conexion = obtener_conexion()
                        if conexion:
                            cursor = conexion.cursor()
                            cursor.execute("""
                                INSERT INTO miembrogapc 
                                (nombre, telefono, dui, correo, contrasena, id_grupo, id_rol)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                nombre, 
                                telefono, 
                                dui, 
                                correo if correo else None,
                                contrasena if contrasena else None,
                                id_grupo,
                                roles_dict[rol_seleccionado]
                            ))
                            conexion.commit()
                            cursor.close()
                            conexion.close()
                            st.success(f"✅ Miembro {nombre} agregado exitosamente!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar miembro: {e}")
                else:
                    st.warning("⚠️ Por favor completa los campos obligatorios")
    
    with tab3:
        st.subheader("Estadísticas de Miembros")
        
        miembros = obtener_miembros_grupo(id_grupo)
        if miembros:
            df_miembros = pd.DataFrame(miembros)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de roles
                if 'tipo_rol' in df_miembros.columns:
                    roles_count = df_miembros['tipo_rol'].value_counts()
                    st.bar_chart(roles_count)
                    st.caption("Distribución de Roles")
            
            with col2:
                # Métricas adicionales
                st.metric("Miembros con teléfono", len(df_miembros))
                st.metric("Miembros con correo", df_miembros['correo'].notna().sum())
                st.metric("Miembros con DUI", df_miembros['dui'].notna().sum())
        
        else:
            st.info("No hay datos para mostrar estadísticas")

# FUNCIÓN DE DASHBOARD MÁS COMPACTO (ACTUALIZADA)
def mostrar_dashboard_principal():
    """Muestra el dashboard principal más compacto"""
    
    usuario = st.session_state.usuario
    
    # Obtener estadísticas reales
    id_grupo_usuario = usuario.get('id_grupo')
    estadisticas = obtener_estadisticas_reales(id_grupo_usuario)
    
    # SIDEBAR MÁS COMPACTO
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.image("https://via.placeholder.com/100x30/6f42c1/white?text=GAPC", width=100)
        st.markdown("---")
        st.write(f"**👤 {usuario['nombre']}**")
        st.write(f"**🎭 {usuario['tipo_rol']}**")
        st.write(f"**🏢 Grupo #{usuario.get('id_grupo', 1)}**")
        
        if 'correo' in usuario:
            st.write("**🔐 Modo Real**")
        else:
            st.write("**🧪 Modo Prueba**")
            
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Actualizar", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("🚪 Salir", use_container_width=True):
                st.session_state.usuario = None
                st.session_state.current_module = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CONTENIDO PRINCIPAL MÁS COMPACTO
    # Header de bienvenida más pequeño
    st.markdown(f'''
    <div class="welcome-message">
        <h4>¡Bienvenido/a, {usuario['nombre']}!</h4>
        <p>{usuario['tipo_rol']} - Grupo #{usuario.get('id_grupo', 1)}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # SALDO ACTUAL - MÁS COMPACTO
    st.markdown("### 💰 Resumen Financiero")
    
    st.markdown(f'''
    <div class="saldo-card">
        <h4>SALDO ACTUAL DEL GRUPO</h4>
        <h3>${estadisticas['saldo_actual']:,.2f}</h3>
        <p>Total acumulado de aportes</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # MÉTRICAS RÁPIDAS EN FILA MÁS COMPACTA
    st.markdown("### 📊 Estadísticas Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <p><strong>👥 MIEMBROS</strong></p>
            <h4>{estadisticas['total_miembros']}</h4>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <p><strong>💳 PRÉSTAMOS</strong></p>
            <h4>{estadisticas['prestamos_activos']}</h4>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <p><strong>📅 REUNIONES</strong></p>
            <h4>{estadisticas['reuniones_mes']}</h4>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <p><strong>📈 ASISTENCIA</strong></p>
            <h4>92%</h4>
        </div>
        ''', unsafe_allow_html=True)
    
    # BOTONES DE MÓDULOS MÁS COMPACTOS
    st.markdown("### 🚀 Módulos del Sistema")
    
    # Primera fila de botones compactos
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👥 **Miembros**\nGestión", use_container_width=True, key="miembros"):
            st.session_state.current_module = "miembros"
            st.rerun()
    
    with col2:
        if st.button("📅 **Reuniones**\nCalendario", use_container_width=True, key="reuniones"):
            st.info("🔧 Módulo Reuniones - En desarrollo")
    
    with col3:
        if st.button("💰 **Aportes**\nAhorros", use_container_width=True, key="aportes"):
            st.info("🔧 Módulo Aportes - En desarrollo")
    
    with col4:
        if st.button("💳 **Préstamos**\nGestionar", use_container_width=True, key="prestamos"):
            st.info("🔧 Módulo Préstamos - En desarrollo")
    
    # Segunda fila de botones compactos
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⚠️ **Multas**\nSanciones", use_container_width=True, key="multas"):
            st.info("🔧 Módulo Multas - En desarrollo")
    
    with col2:
        if st.button("📊 **Reportes**\nEstadísticas", use_container_width=True, key="reportes"):
            st.info("🔧 Módulo Reportes - En desarrollo")
    
    with col3:
        if st.button("🔄 **Cierre**\nPeríodo", use_container_width=True, key="cierre"):
            st.info("🔧 Módulo Cierre - En desarrollo")
    
    with col4:
        if st.button("⚙️ **Configuración**\nAjustes", use_container_width=True, key="configuracion"):
            st.info("🔧 Módulo Configuración - En desarrollo")
    
    # Información del sistema más compacta
    st.markdown("---")
    st.markdown(f'<p class="compact-text">*Última actualización: {datetime.now().strftime("%d/%m/%Y %H:%M")}*</p>', unsafe_allow_html=True)

# APLICACIÓN PRINCIPAL ACTUALIZADA
def main():
    # Inicializar session state para módulos
    if 'current_module' not in st.session_state:
        st.session_state.current_module = None
    
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        if st.session_state.current_module == "miembros":
            mostrar_modulo_miembros()
        else:
            mostrar_dashboard_principal()

if __name__ == "__main__":
    main()
