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
        height: 220px; /* Aumentada la altura para más espacio */
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
        margin-bottom: 1rem; /* Más espacio antes del botón */
    }
    
    /* Botones morados en recuadro con más espacio */
    .purple-button-container {
        background: linear-gradient(90deg, #6f42c1, #5a32a3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem; /* Más padding vertical */
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem; /* Más espacio arriba */
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        font-size: 1rem;
        min-height: 45px; /* Altura mínima consistente */
    }
    
    .purple-button-container:hover {
        background: linear-gradient(90deg, #5a32a3, #4a2a8c);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(106, 66, 193, 0.3);
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
    
    /* Mejoras para los botones de Streamlit */
    .stButton button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Más espacio entre elementos */
    .module-spacing {
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)


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
        
        # Botones del menú usando st.button directamente
        if st.button("🏠 Inicio", use_container_width=True, type="primary"):
            st.rerun()
            
        if st.button("👥 Miembros", use_container_width=True):
            st.rerun()
            
        if st.button("📅 Reuniones", use_container_width=True):
            st.rerun()
            
        if st.button("💰 Aportes", use_container_width=True):
            st.rerun()
            
        if st.button("💳 Préstamos", use_container_width=True):
            st.rerun()
            
        if st.button("⚠️ Multas", use_container_width=True):
            st.rerun()
            
        if st.button("📊 Reportes", use_container_width=True):
            st.rerun()
            
        if st.button("🔄 Cierre de Ciclo", use_container_width=True):
            st.rerun()
            
        if st.button("⚙️ Configuración", use_container_width=True):
            st.rerun()
        
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Botón cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario = None
            st.rerun()


# ==========================================
# DASHBOARD
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
            <div class="purple-button-container" onclick="alert('Abriendo Miembros')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Módulo Reuniones
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #6f42c1;">📅</div>
                <h4 style="color: #5a32a3; margin: 0.5rem 0;">Reuniones</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Calendario y registro de reuniones</p>
            </div>
            <div class="purple-button-container" onclick="alert('Abriendo Reuniones')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Módulo Aportes
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #10b981;">💰</div>
                <h4 style="color: #5a32a3; margin: 1.1rem 0;">Aportes</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Registro de aportes y ahorros</p>
            </div>
            <div class="purple-button-container" onclick="alert('Abriendo Aportes')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
            <div class="purple-button-container" onclick="alert('Abriendo Préstamos')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Módulo Multas
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #ef4444;">⚠️</div>
                <h4 style="color: #5a32a3; margin: 1.1rem 0;">Multas</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Control de multas y sanciones</p>
            </div>
            <div class="purple-button-container" onclick="alert('Abriendo Multas')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Módulo Reportes
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #5a32a3;">📊</div>
                <h4 style="color: #5a32a3; margin: 0.5rem 0;">Reportes</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Reportes financieros y estadísticas</p>
            </div>
            <div class="purple-button-container" onclick="alert('Abriendo Reportes')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Fila 3
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Módulo Cierre de Período
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #4c2a85;">🔄</div>
                <h4 style="color: #5a32a3; margin: 0.5rem 0;">Cierre de Período</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Cierre de período y reparto</p>
            </div>
            <div class="purple-button-container" onclick="alert('Abriendo Cierre de Período')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Módulo Configuración
        st.markdown("""
        <div class="module-card">
            <div class="module-content">
                <div class="module-icon" style="background-color: #64748b;">⚙️</div>
                <h4 style="color: #5a32a3; margin: 1.1rem 0;">Configuración</h4>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Ajustes del grupo y reglamento</p>
            </div>
            <div class="purple-button-container" onclick="alert('Abriendo Configuración')">
                Abrir
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sección de Estadísticas Rápidas
    st.markdown("<h2 style='color: #5a32a3; margin-top: 2rem;'>📈 Estadísticas Rápidas</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card stat-purple">
            <p style="margin: 0; font-size: 0.8rem; color: #64748b;">Asistencia Promedio</p>
            <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #5a32a3;">92%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card stat-green">
            <p style="margin: 0; font-size: 0.8rem; color: #065f46;">Total Ahorrado (Este Mes)</p>
            <p style="margin: 0; font-size: 1.2rem; font-weight: bold; color: #065f46;">$3,250.00</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card stat-red">
            <p style="margin: 0; font-size: 0.8rem; color: #991b1b;">Préstamos en Mora</p>
            <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #991b1b;">2</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card stat-purple">
            <p style="margin: 0; font-size: 0.8rem; color: #64748b;">Reuniones (Este Mes)</p>
            <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #5a32a3;">4</p>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# FLUJO PRINCIPAL
# ==========================================
if st.session_state.usuario is None:
    mostrar_login()
else:
    mostrar_dashboard()

















