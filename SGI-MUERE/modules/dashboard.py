import streamlit as st
from datetime import datetime

def mostrar_dashboard_principal():
    """Muestra el dashboard principal más compacto"""
    
    usuario = st.session_state.usuario
    
    # Obtener estadísticas reales
    from app import obtener_estadisticas_reales
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

    # Segunda fila de botones compactos
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
    
    # Información del sistema más compacta
    st.markdown("---")
    st.markdown(f'<p class="compact-text">*Última actualización: {datetime.now().strftime("%d/%m/%Y %H:%M")}*</p>', unsafe_allow_html=True)