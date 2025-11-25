def mostrar_dashboard_principal():
    """Muestra el dashboard principal más compacto y optimizado"""

    usuario = st.session_state.usuario
    id_grupo_usuario = usuario.get('id_grupo')

    # Obtener estadísticas reales (aunque ya no se usan en pantalla)
    estadisticas = obtener_estadisticas_reales(id_grupo_usuario)


    # ----------------- HEADER -------------------
    st.markdown(f"""
    <div class="welcome-message">
        <h4>¡Bienvenido/a, {usuario['nombre']}!</h4>
        <p>{usuario['tipo_rol']} - Grupo #{id_grupo_usuario}</p>
    </div>
    """, unsafe_allow_html=True)

    # ----------------- (SECCIÓN BORRADA) -------------------
    # Eliminado: Resumen financiero
    # Eliminado: Tarjeta de saldo
    # Eliminado: Estadísticas rápidas
    # Eliminadas: cuatro métricas

    # ----------------- MÓDULOS -------------------
    st.markdown("### 🚀 Módulos del Sistema")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("👥 **Miembros**\nGestión", use_container_width=True, key="miembros"):
            st.session_state.modulo_actual = 'miembros'
            st.rerun()
    with col2:
        if st.button("📅 **Reuniones**\nCalendario", use_container_width=True, key="reuniones"):
            st.session_state.modulo_actual = 'reuniones'
            st.rerun()
    with col3:
        if st.button("💰 **Aportes**\nAhorros", use_container_width=True, key="aportes"):
            st.session_state.modulo_actual = 'aportes'
            st.rerun()
    with col4:
        if st.button("💳 **Préstamos**\nGestionar", use_container_width=True, key="prestamos"):
            st.session_state.modulo_actual = 'prestamos'
            st.rerun()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("⚠️ **Multas**\nSanciones", use_container_width=True, key="multas"):
            st.session_state.modulo_actual = 'multas'
            st.rerun()
    with col2:
        if st.button("📊 **Reportes**\nEstadísticas", use_container_width=True, key="reportes"):
            st.session_state.modulo_actual = 'reportes'
            st.rerun()
    with col3:
        if st.button("🔄 **Cierre**\nPeríodo", use_container_width=True, key="cierre"):
            st.session_state.modulo_actual = 'cierre'
            st.rerun()
    with col4:
        if st.button("⚙️ **Configuración**\nAjustes", use_container_width=True, key="configuracion"):
            st.session_state.modulo_actual = 'configuracion'
            st.rerun()

    # ----------------- FOOTER -------------------
    st.markdown("---")
    st.markdown(
        f'<p class="compact-text">*Última actualización: {datetime.now().strftime("%d/%m/%Y %H:%M")}*</p>',
        unsafe_allow_html=True
    )

