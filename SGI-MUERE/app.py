import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION STATE
# ==========================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "modulo_actual" not in st.session_state:
    st.session_state.modulo_actual = "dashboard"

# ==========================================
# CONEXIÓN A MYSQL (Clever Cloud)
# ==========================================
def obtener_conexion():
    try:
        conexion = pymysql.connect(
            host="bhzcn4gxgbe5tcxihqd1-mysql.services.clever-cloud.com",
            user="usv5pnvafxbrw5hs",
            password="WiOSztB38WxsKuXjnQgT",
            database="bhzcn4gxgbe5tcxihqd1",
            port=3306,
            cursorclass=pymysql.cursors.DictCursor,
            charset="utf8mb4"
        )
        return conexion
    except Exception as e:
        st.error(f"❌ Error conectando a la BD: {e}")
        return None

# ==========================================
# LOGIN REAL
# ==========================================
def verificar_login(correo, contrasena):
    try:
        conexion = obtener_conexion()
        if not conexion:
            return None

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT m.id_miembro, m.nombre, m.correo, m.contrasena, 
                   m.id_grupo, r.tipo_rol
            FROM miembrogapc m
            JOIN rol r ON m.id_rol = r.id_rol
            WHERE m.correo = %s
        """, (correo,))

        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario and usuario["contrasena"] == contrasena:
            return usuario

        return None

    except Exception as e:
        st.error(f"⚠️ Error verificando login: {e}")
        return None

# ==========================================
# ESTADÍSTICAS DEL DASHBOARD
# ==========================================
def obtener_estadisticas(id_grupo):
    stats = {
        "total_miembros": 0,
        "prestamos_activos": 0,
        "reuniones_mes": 0,
        "saldo_actual": 0
    }

    try:
        conexion = obtener_conexion()
        if not conexion:
            return stats

        cursor = conexion.cursor()

        # Total miembros
        cursor.execute("SELECT COUNT(*) AS total FROM miembrogapc WHERE id_grupo=%s", (id_grupo,))
        stats["total_miembros"] = cursor.fetchone()["total"]

        # Préstamos activos
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM prestamo p
            JOIN miembrogapc m ON p.id_miembro = m.id_miembro
            WHERE p.estado='aprobado' AND m.id_grupo=%s
        """, (id_grupo,))
        stats["prestamos_activos"] = cursor.fetchone()["total"]

        # Reuniones este mes (corrección: id_grupo)
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reunion
            WHERE id_grupo=%s
            AND MONTH(fecha)=MONTH(CURDATE())
            AND YEAR(fecha)=YEAR(CURDATE())
        """, (id_grupo,))
        stats["reuniones_mes"] = cursor.fetchone()["total"]

        # Saldo actual (corrección: id_grupo)
        cursor.execute("""
            SELECT COALESCE(SUM(a.monto), 0) AS total
            FROM aporte a
            JOIN reunion r ON a.id_reunion=r.id_reunion
            WHERE r.id_grupo=%s
        """, (id_grupo,))
        stats["saldo_actual"] = float(cursor.fetchone()["total"])

        cursor.close()
        conexion.close()
        return stats

    except Exception as e:
        st.error(f"⚠️ Error cargando estadísticas: {e}")
        return stats

# ==========================================
# ESTILOS CSS PERSONALIZADOS
# ==========================================
def aplicar_estilos():
    st.markdown("""
    <style>
    /* Fondo general */
    .main .block-container {
        background-color: #f8fafc;
        padding-top: 2rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] > div:first-child {
        background-color: white;
        padding: 2rem 1rem;
    }
    
    /* Tarjetas con gradientes */
    .metric-card-purple {
        background: linear-gradient(90deg, #6f42c1, #5a32a3);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    /* Módulos del sistema */
    .module-card {
        background-color: white;
        border: 2px solid #c9b3f5;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 4rem;
    }
    
    .module-icon {
        width: 60px;
        height: 60px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 28px;
        color: white;
    }
    
    /* Contenido del módulo con más espacio */
    .module-content {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    /* Botones morados en recuadro con más espacio */
    .purple-button-container {
        background: linear-gradient(90deg, #6f42c1, #5a32a3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        font-size: 1rem;
        min-height: 45px;
    }
    
    .purple-button-container:hover {
        background: linear-gradient(90deg, #5a32a3, #4a2a8c);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(106, 66, 193, 0.3);
    }
    
    /* Botones de opciones en módulos */
    .option-button {
        background: linear-gradient(90deg, #6f42c1, #5a32a3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 1rem;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        width: 100%;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .option-button:hover {
        background: linear-gradient(90deg, #5a32a3, #4a2a8c);
        transform: translateY(-2px);
    }
    
    /* Estadísticas rápidas */
    .stat-card {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .stat-purple {
        background-color: #f3ebff;
        border: 1px solid #c9b3f5;
    }
    
    .stat-green {
        background-color: #d1fae5;
        border: 1px solid #a7f3d0;
    }
    
    .stat-red {
        background-color: #fee2e2;
        border: 1px solid #fecaca;
    }
    
    /* Botones del sidebar */
    .sidebar-button {
        width: 100%;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        border: 2px solid #c9b3f5;
        background-color: white;
        color: #6f42c1;
        text-align: left;
        font-weight: bold;
        cursor: pointer;
    }
    
    .sidebar-button.active {
        background: linear-gradient(90deg, #6f42c1, #5a32a3);
        color: white;
        border: none;
    }
    
    .sidebar-logout {
        background-color: #64748b;
        color: white;
        border: none;
    }
    
    /* Perfil de usuario */
    .user-profile {
        background-color: #f3ebff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    
    .user-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: #a78bfa;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 20px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# MÓDULO DE MIEMBROS
# ==========================================
def mostrar_modulo_miembros():
    st.markdown("<h1 style='color: #5a32a3;'>👥 Gestión de Miembros</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Agregar Nuevo Miembro")
        with st.form("form_agregar_miembro"):
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")
            direccion = st.text_area("Dirección")
            
            if st.form_submit_button("➕ Agregar Miembro", use_container_width=True):
                if nombre and correo:
                    st.success(f"Miembro {nombre} agregado exitosamente")
                else:
                    st.error("Por favor complete todos los campos obligatorios")
    
    with col2:
        st.markdown("### 📊 Opciones de Miembros")
        
        if st.button("👀 Ver Registro de Miembros", use_container_width=True, type="primary"):
            st.info("Mostrando registro de miembros...")
            # Aquí iría la lógica para mostrar la tabla de miembros
        
        if st.button("✏️ Editar Información de Miembro", use_container_width=True):
            st.info("Funcionalidad de edición de miembros")
        
        if st.button("📋 Reporte de Miembros", use_container_width=True):
            st.info("Generando reporte de miembros...")
        
        if st.button("📈 Estadísticas de Miembros", use_container_width=True):
            st.info("Mostrando estadísticas de miembros...")

# ==========================================
# MÓDULO DE REUNIONES
# ==========================================
def mostrar_modulo_reuniones():
    st.markdown("<h1 style='color: #5a32a3;'>📅 Gestión de Reuniones</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🗓️ Programar Reunión")
        with st.form("form_programar_reunion"):
            fecha = st.date_input("Fecha de la reunión")
            hora = st.time_input("Hora de la reunión")
            lugar = st.text_input("Lugar")
            tema = st.text_area("Tema principal")
            
            if st.form_submit_button("📅 Programar Reunión", use_container_width=True):
                st.success("Reunión programada exitosamente")
    
    with col2:
        st.markdown("### 📋 Opciones de Reuniones")
        
        if st.button("📊 Calendario de Reuniones", use_container_width=True, type="primary"):
            st.info("Mostrando calendario de reuniones...")
        
        if st.button("✅ Registrar Asistencia", use_container_width=True):
            st.info("Registrando asistencia...")
        
        if st.button("📝 Acta de Reunión", use_container_width=True):
            st.info("Generando acta de reunión...")
        
        if st.button("📈 Historial de Reuniones", use_container_width=True):
            st.info("Mostrando historial de reuniones...")

# ==========================================
# MÓDULO DE APORTES
# ==========================================
def mostrar_modulo_aportes():
    st.markdown("<h1 style='color: #5a32a3;'>💰 Gestión de Aportes</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💵 Registrar Aporte")
        with st.form("form_registrar_aporte"):
            miembro = st.selectbox("Seleccionar miembro", ["Miembro 1", "Miembro 2", "Miembro 3"])
            monto = st.number_input("Monto del aporte", min_value=0.0, format="%.2f")
            fecha = st.date_input("Fecha del aporte")
            concepto = st.text_input("Concepto")
            
            if st.form_submit_button("💳 Registrar Aporte", use_container_width=True):
                st.success(f"Aporte de ${monto:.2f} registrado exitosamente")
    
    with col2:
        st.markdown("### 📊 Opciones de Aportes")
        
        if st.button("📋 Historial de Aportes", use_container_width=True, type="primary"):
            st.info("Mostrando historial de aportes...")
        
        if st.button("📈 Estadísticas de Ahorro", use_container_width=True):
            st.info("Mostrando estadísticas de ahorro...")
        
        if st.button("💰 Saldos Individuales", use_container_width=True):
            st.info("Consultando saldos individuales...")
        
        if st.button("📄 Reporte de Aportes", use_container_width=True):
            st.info("Generando reporte de aportes...")

# ==========================================
# MÓDULO DE PRÉSTAMOS
# ==========================================
def mostrar_modulo_prestamos():
    st.markdown("<h1 style='color: #5a32a3;'>💳 Gestión de Préstamos</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🏦 Solicitar Préstamo")
        with st.form("form_solicitar_prestamo"):
            miembro = st.selectbox("Seleccionar miembro", ["Miembro 1", "Miembro 2", "Miembro 3"])
            monto = st.number_input("Monto del préstamo", min_value=0.0, format="%.2f")
            plazo = st.selectbox("Plazo en meses", [3, 6, 12, 24])
            proposito = st.text_area("Propósito del préstamo")
            
            if st.form_submit_button("📝 Solicitar Préstamo", use_container_width=True):
                st.success("Solicitud de préstamo enviada para revisión")
    
    with col2:
        st.markdown("### 📊 Opciones de Préstamos")
        
        if st.button("📋 Préstamos Activos", use_container_width=True, type="primary"):
            st.info("Mostrando préstamos activos...")
        
        if st.button("💵 Registrar Pago", use_container_width=True):
            st.info("Registrando pago de préstamo...")
        
        if st.button("⚠️ Préstamos Vencidos", use_container_width=True):
            st.info("Mostrando préstamos vencidos...")
        
        if st.button("📈 Historial de Préstamos", use_container_width=True):
            st.info("Mostrando historial de préstamos...")

# ==========================================
# MÓDULO DE MULTAS
# ==========================================
def mostrar_modulo_multas():
    st.markdown("<h1 style='color: #5a32a3;'>⚠️ Gestión de Multas</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### ⚠️ Registrar Multa")
        with st.form("form_registrar_multa"):
            miembro = st.selectbox("Seleccionar miembro", ["Miembro 1", "Miembro 2", "Miembro 3"])
            monto = st.number_input("Monto de la multa", min_value=0.0, format="%.2f")
            motivo = st.selectbox("Motivo", ["Falta de asistencia", "Pago tardío", "Otro"])
            descripcion = st.text_area("Descripción detallada")
            
            if st.form_submit_button("⚖️ Registrar Multa", use_container_width=True):
                st.success("Multa registrada exitosamente")
    
    with col2:
        st.markdown("### 📊 Opciones de Multas")
        
        if st.button("📋 Multas Pendientes", use_container_width=True, type="primary"):
            st.info("Mostrando multas pendientes...")
        
        if st.button("💵 Registrar Pago de Multa", use_container_width=True):
            st.info("Registrando pago de multa...")
        
        if st.button("📈 Historial de Multas", use_container_width=True):
            st.info("Mostrando historial de multas...")
        
        if st.button("⚙️ Configurar Multas", use_container_width=True):
            st.info("Configurando parámetros de multas...")

# ==========================================
# MÓDULO DE REPORTES
# ==========================================
def mostrar_modulo_reportes():
    st.markdown("<h1 style='color: #5a32a3;'>📊 Reportes y Estadísticas</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Reporte Financiero General", use_container_width=True, type="primary"):
            st.info("Generando reporte financiero general...")
        
        if st.button("👥 Reporte de Miembros", use_container_width=True):
            st.info("Generando reporte de miembros...")
    
    with col2:
        if st.button("💳 Reporte de Préstamos", use_container_width=True):
            st.info("Generando reporte de préstamos...")
        
        if st.button("💰 Reporte de Aportes", use_container_width=True):
            st.info("Generando reporte de aportes...")
    
    with col3:
        if st.button("📅 Reporte de Reuniones", use_container_width=True):
            st.info("Generando reporte de reuniones...")
        
        if st.button("⚠️ Reporte de Multas", use_container_width=True):
            st.info("Generando reporte de multas...")

# ==========================================
# MÓDULO DE CIERRE DE PERÍODO
# ==========================================
def mostrar_modulo_cierre():
    st.markdown("<h1 style='color: #5a32a3;'>🔄 Cierre de Período</h1>", unsafe_allow_html=True)
    
    st.warning("⚠️ Esta acción es irreversible. Asegúrese de tener respaldos.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Estado Actual")
        st.info("**Período actual:** Enero 2024")
        st.info("**Total de miembros:** 25")
        st.info("**Saldo general:** $15,450.00")
        st.info("**Préstamos activos:** 8")
    
    with col2:
        st.markdown("### 🔄 Opciones de Cierre")
        
        if st.button("📋 Verificar Estado para Cierre", use_container_width=True, type="primary"):
            st.success("Verificación completada. Sistema listo para cierre.")
        
        if st.button("💰 Calcular Reparto", use_container_width=True):
            st.info("Calculando reparto de utilidades...")
        
        if st.button("🔄 Ejecutar Cierre de Período", use_container_width=True):
            st.success("Cierre de período ejecutado exitosamente")
        
        if st.button("📄 Generar Acta de Cierre", use_container_width=True):
            st.info("Generando acta de cierre...")

# ==========================================
# MÓDULO DE CONFIGURACIÓN
# ==========================================
def mostrar_modulo_configuracion():
    st.markdown("<h1 style='color: #5a32a3;'>⚙️ Configuración del Sistema</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Información General", "👥 Roles y Permisos", "💰 Parámetros Financieros", "🔔 Notificaciones"])
    
    with tab1:
        st.markdown("### Información del Grupo")
        with st.form("form_info_grupo"):
            nombre_grupo = st.text_input("Nombre del grupo", value="Grupo Las Mariposas")
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("💾 Guardar Información", use_container_width=True):
                st.success("Información guardada exitosamente")
    
    with tab2:
        st.markdown("### Gestión de Roles")
        st.selectbox("Asignar rol", ["Administrador", "Presidente", "Tesorero", "Secretario", "Miembro"])
        st.button("🔄 Actualizar Roles", use_container_width=True)
    
    with tab3:
        st.markdown("### Parámetros Financieros")
        st.number_input("Monto mínimo de aporte", value=50.0)
        st.number_input("Tasa de interés de préstamos (%)", value=5.0)
        st.button("💾 Guardar Parámetros", use_container_width=True)
    
    with tab4:
        st.markdown("### Configuración de Notificaciones")
        st.checkbox("Notificaciones por email", value=True)
        st.checkbox("Recordatorios de reuniones", value=True)
        st.checkbox("Alertas de pagos vencidos", value=True)
        st.button("🔔 Guardar Preferencias", use_container_width=True)

# ==========================================
# FORMULARIO DE LOGIN
# ==========================================
def mostrar_login():
    aplicar_estilos()
    
    st.markdown("<h1 style='text-align: center; color: #6f42c1;'>🏠 Sistema GAPC</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("<div style='background-color: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #5a32a3;'>Iniciar Sesión</h2>", unsafe_allow_html=True)
            
            correo = st.text_input("📧 Correo")
            contrasena = st.text_input("🔒 Contraseña", type="password")
            
            if st.button("Ingresar", use_container_width=True):
                usuario = verificar_login(correo, contrasena)
                if usuario:
                    st.success(f"Bienvenido {usuario['nombre']}!")
                    st.session_state.usuario = usuario
                    st.session_state.modulo_actual = "dashboard"
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
                    
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
def mostrar_sidebar():
    usuario = st.session_state.usuario
    
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style='background: linear-gradient(90deg, #6f42c1, #5a32a3); padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: white; margin: 0;'>🏦 GAPC</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Perfil de usuario
        st.markdown(f"""
        <div class="user-profile">
            <div class="user-avatar">👤</div>
            <div>
                <div style="font-weight: bold; color: #5a32a3;">{usuario['nombre']}</div>
                <div style="font-size: 0.8rem; color: #64748b;">{usuario['tipo_rol']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # Menú de navegación
        st.markdown("<p style='font-weight: bold; color: #6f42c1;'>📋 Menú Principal</p>", unsafe_allow_html=True)
        
        # Botón para volver al dashboard
        if st.button("🏠 Volver al Inicio", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "dashboard"
            st.rerun()
            
        # Botones de módulos
        modulos = [
            ("👥 Miembros", "miembros"),
            ("📅 Reuniones", "reuniones"),
            ("💰 Aportes", "aportes"),
            ("💳 Préstamos", "prestamos"),
            ("⚠️ Multas", "multas"),
            ("📊 Reportes", "reportes"),
            ("🔄 Cierre de Ciclo", "cierre"),
            ("⚙️ Configuración", "configuracion")
        ]
        
        for nombre, modulo in modulos:
            if st.button(nombre, use_container_width=True):
                st.session_state.modulo_actual = modulo
                st.rerun()
        
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Botón cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario = None
            st.session_state.modulo_actual = "dashboard"
            st.rerun()

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
def mostrar_dashboard():
    aplicar_estilos()
    usuario = st.session_state.usuario
    
    # Mostrar sidebar
    mostrar_sidebar()
    
    # Título principal
    st.markdown(f"<h1 style='color: #5a32a3;'>👋 ¡Bienvenido/a, {usuario['nombre']}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748b; font-size: 1.2rem;'>{usuario['tipo_rol']} - Grupo {usuario['id_grupo']}</p>", unsafe_allow_html=True)
    
    # Obtener estadísticas
    stats = obtener_estadisticas(usuario["id_grupo"])
    
    # Sección: Resumen Financiero - SOLO SALDO ACTUAL
    st.markdown("<h2 style='color: #5a32a3;'>📊 Resumen Financiero</h2>", unsafe_allow_html=True)
    
    # Solo Saldo Actual
    st.markdown(f"""
    <div class="metric-card-purple">
        <p style="margin: 0; font-size: 1rem;">💰 SALDO ACTUAL</p>
        <h2 style="margin: 0.5rem 0;">${stats['saldo_actual']:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sección: Módulos del Sistema
    st.markdown("<h2 style='color: #5a32a3; margin-top: 2rem;'>📋 Módulos del Sistema</h2>", unsafe_allow_html=True)
    
    # Grid de módulos (3 columnas x 3 filas)
    # Fila 1
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Módulo Miembros
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background: linear-gradient(90deg, #8b5cf6, #6f42c1);">👥</div>
                <h4 style="color: #5a32a3; margin: 1.1rem 0;">Miembros</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Gestión de miembros del grupo</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir", key="btn_miembros", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "miembros"
            st.rerun()
    
    with col2:
        # Módulo Reuniones
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #6f42c1;">📅</div>
                <h4 style="color: #5a32a3; margin: 0.5rem 0;">Reuniones</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Calendario y registro de reuniones</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir", key="btn_reuniones", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "reuniones"
            st.rerun()
    
    with col3:
        # Módulo Aportes
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #10b981;">💰</div>
                <h4 style="color: #5a32a3; margin: 1.1rem 0;">Aportes</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Registro de aportes y ahorros</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir", key="btn_aportes", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "aportes"
            st.rerun()
    
    # Fila 2
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Módulo Préstamos
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #eab308;">💳</div>
                <h4 style="color: #5a32a3; margin: 1.1rem 0;">Préstamos</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Gestión de préstamos y pagos</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir", key="btn_prestamos", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "prestamos"
            st.rerun()
    
    with col2:
        # Módulo Multas
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #ef4444;">⚠️</div>
                <h4 style="color: #5a32a3; margin: 1.1rem 0;">Multas</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Control de multas y sanciones</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir", key="btn_multas", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "multas"
            st.rerun()
    
    with col3:
        # Módulo Reportes
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #5a32a3;">📊</div>
                <h4 style="color: #5a32a3; margin: 0.5rem 0;">Reportes</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Reportes financieros y estadísticas</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir", key="btn_reportes", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "reportes"
            st.rerun()
    
    # Fila 3
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Módulo Cierre de Período
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #4c2a85;">🔄</div>
                <h4 style="color: #5a32a3; margin: 0.4rem 0;">Cierre de Período</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Cierre de período y reparto</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir", key="btn_cierre", use_container_width=True, type="primary"):
            st.session_state.modulo_actual = "cierre"
            st.rerun()
    
    with col2:
        # Módulo Configuración
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon
