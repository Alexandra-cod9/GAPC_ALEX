import streamlit as st
from datetime import datetime
from utils.navegacion import es_promotora
from modules.configuracion import obtener_conexion

def obtener_distrito_promotora(usuario):
    """Obtiene el distrito asignado a la promotora a través de su grupo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener el distrito a través del grupo de la promotora
            cursor.execute("""
                SELECT 
                    d.id_distrito,
                    d.nombre_distrito,
                    m.nombre_municipio,
                    dep.nombre_departamento
                FROM miembrogapc mg
                JOIN grupo g ON mg.id_grupo = g.id_grupo
                JOIN distrito d ON g.id_distrito = d.id_distrito
                JOIN municipio m ON d.id_municipio = m.id_municipio
                JOIN departamento dep ON m.id_departamento = dep.id_departamento
                WHERE mg.id_miembro = %s
            """, (usuario.get('id_miembro'),))
            
            distrito = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            return distrito
    except Exception as e:
        st.error(f"❌ Error al obtener distrito: {e}")
    
    return None

def mostrar_dashboard_principal():
    """Muestra el dashboard principal más compacto y optimizado"""
    usuario = st.session_state.usuario
    id_grupo_usuario = usuario.get('id_grupo')
  
    # ----------------- SIDEBAR -------------------
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.image("https://via.placeholder.com/100x30/6f42c1/white?text=GAPC", width=100)
        st.markdown("---")
        st.write(f"**👤 {usuario['nombre']}**")
        st.write(f"**🎭 {usuario['tipo_rol']}**")
        st.write(f"**🏢 Grupo #{id_grupo_usuario}**")
        st.write("**🔐 Modo Real**" if 'correo' in usuario else "**🧪 Modo Prueba**")
        st.markdown("---")
        
        # Información específica para promotoras
        if es_promotora(usuario):
            st.markdown("### 👩‍💼 Panel Promotora")
            distrito = obtener_distrito_promotora(usuario)
            
            if distrito:
                st.info(f"""
                📍 **Tu distrito asignado:**
                - **Distrito:** {distrito['nombre_distrito']}
                - **Municipio:** {distrito['nombre_municipio']}
                - **Departamento:** {distrito['nombre_departamento']}
                """)
            else:
                st.warning("⚠️ No se encontró distrito asignado")
            
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
    
    # ----------------- HEADER -------------------
    st.markdown(f"""
    <div class="welcome-message">
        <h4>¡Bienvenido/a, {usuario['nombre']}!</h4>
        <p>{usuario['tipo_rol']} - Grupo #{id_grupo_usuario}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ----------------- ACCIONES ESPECIALES PARA PROMOTORA -------------------
    if es_promotora(usuario):
        st.markdown("---")
        st.markdown("### 👩‍💼 Acciones de Promotora")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Crear Nuevo Grupo", use_container_width=True, type="primary"):
                st.info("🚧 Funcionalidad en desarrollo: Crear nuevo grupo")
                # Aquí puedes agregar la lógica para crear grupo
        
        with col2:
            if st.button("📊 Reporte por Grupo", use_container_width=True, type="primary"):
                st.info("🚧 Funcionalidad en desarrollo: Reporte por grupo")
                # Aquí puedes agregar la lógica para mostrar reportes
        
        with col3:
            if st.button("🗺️ Ver Grupos del Distrito", use_container_width=True, type="primary"):
                mostrar_grupos_distrito(usuario)
    
    # ----------------- MÓDULOS -------------------
    st.markdown("---")
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

def mostrar_grupos_distrito(usuario):
    """Muestra todos los grupos del distrito de la promotora"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener el distrito de la promotora
            cursor.execute("""
                SELECT g.id_distrito
                FROM miembrogapc mg
                JOIN grupo g ON mg.id_grupo = g.id_grupo
                WHERE mg.id_miembro = %s
            """, (usuario.get('id_miembro'),))
            
            resultado = cursor.fetchone()
            
            if resultado:
                id_distrito = resultado['id_distrito']
                
                # Obtener todos los grupos del distrito
                cursor.execute("""
                    SELECT 
                        g.id_grupo,
                        g.nombre_grupo,
                        g.nombre_comunidad,
                        g.fecha_formacion,
                        COUNT(DISTINCT m.id_miembro) as total_miembros
                    FROM grupo g
                    LEFT JOIN miembrogapc m ON g.id_grupo = m.id_grupo
                    WHERE g.id_distrito = %s
                    GROUP BY g.id_grupo
                    ORDER BY g.nombre_grupo
                """, (id_distrito,))
                
                grupos = cursor.fetchall()
                
                cursor.close()
                conexion.close()
                
                if grupos:
                    st.subheader("🗺️ Grupos en tu Distrito")
                    
                    for grupo in grupos:
                        with st.expander(f"**{grupo['nombre_grupo']}** - {grupo['nombre_comunidad']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**ID Grupo:** {grupo['id_grupo']}")
                                st.write(f"**Fecha Formación:** {grupo['fecha_formacion']}")
                            with col2:
                                st.write(f"**Total Miembros:** {grupo['total_miembros']}")
                else:
                    st.info("No hay grupos registrados en este distrito")
            else:
                st.warning("No se pudo determinar el distrito")
                
    except Exception as e:
        st.error(f"❌ Error al obtener grupos del distrito: {e}")
