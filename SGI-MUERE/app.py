import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'id_grupo' not in st.session_state:
    st.session_state.id_grupo = None

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        color: #6f42c1;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2.5rem;
    }
    .stButton button {
        background-color: #6f42c1;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        border: 2px solid #e0d1f9;
        border-radius: 1rem;
        background: #f8fafc;
    }
    .welcome-message {
        background: linear-gradient(135deg, #6f42c1, #8b5cf6);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Función de conexión a BD - CLEVER CLOUD
def obtener_conexion():
    try:
        conexion = pymysql.connect(
            host='bhzcn4gxgbe5tcxihqd1-mysql.services.clever-cloud.com',  # ⬅️ HOST CLEVER CLOUD
            user='usv5pnvafxbrw5hs',                                      # ⬅️ USUARIO CLEVER CLOUD
            password='WiOSztB38WxsKuXjnQgT',                             # ⬅️ PASSWORD CLEVER CLOUD
            database='bhzcn4gxgbe5tcxihqd1',                             # ⬅️ DATABASE CLEVER CLOUD
            port=3306,                                                   # ⬅️ PUERTO CLEVER CLOUD
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10  # Timeout para evitar esperas largas
        )
        return conexion
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

# Función para obtener estadísticas reales
def obtener_estadisticas_reales(id_grupo=None):
    """Obtiene estadísticas reales de la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            estadisticas = {}
            
            # Total de miembros
            if id_grupo:
                cursor.execute("SELECT COUNT(*) as total FROM miembrogapc WHERE id_grupo = %s", (id_grupo,))
            else:
                cursor.execute("SELECT COUNT(*) as total FROM miembrogapc")
            resultado = cursor.fetchone()
            estadisticas['total_miembros'] = resultado['total'] if resultado else 0
            
            # Préstamos activos (aprobados)
            if id_grupo:
                cursor.execute("""
                    SELECT COUNT(*) as total 
                    FROM prestamo p 
                    JOIN miembrogapc m ON p.id_miembro = m.id_miembro 
                    WHERE m.id_grupo = %s AND p.estado = 'aprobado'
                """, (id_grupo,))
            else:
                cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE estado = 'aprobado'")
            resultado = cursor.fetchone()
            estadisticas['prestamos_activos'] = resultado['total'] if resultado else 0
            
            # Reuniones este mes
            if id_grupo:
                cursor.execute("""
                    SELECT COUNT(*) as total 
                    FROM reunion 
                    WHERE id_gruppo = %s 
                    AND MONTH(fecha) = MONTH(CURDATE()) 
                    AND YEAR(fecha) = YEAR(CURDATE())
                """, (id_grupo,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as total 
                    FROM reunion 
                    WHERE MONTH(fecha) = MONTH(CURDATE()) 
                    AND YEAR(fecha) = YEAR(CURDATE())
                """)
            resultado = cursor.fetchone()
            estadisticas['reuniones_mes'] = resultado['total'] if resultado else 0
            
            # Total de aportes este mes
            if id_grupo:
                cursor.execute("""
                    SELECT COALESCE(SUM(a.monto), 0) as total 
                    FROM aporte a
                    JOIN reunion r ON a.id_reunion = r.id_reunion
                    WHERE r.id_gruppo = %s 
                    AND MONTH(r.fecha) = MONTH(CURDATE()) 
                    AND YEAR(r.fecha) = YEAR(CURDATE())
                """, (id_grupo,))
            else:
                cursor.execute("""
                    SELECT COALESCE(SUM(a.monto), 0) as total 
                    FROM aporte a
                    JOIN reunion r ON a.id_reunion = r.id_reunion
                    WHERE MONTH(r.fecha) = MONTH(CURDATE()) 
                    AND YEAR(r.fecha) = YEAR(CURDATE())
                """)
            resultado = cursor.fetchone()
            estadisticas['total_aportes'] = float(resultado['total']) if resultado and resultado['total'] else 0.0
            
            cursor.close()
            conexion.close()
            return estadisticas
            
    except Exception as e:
        st.error(f"Error al obtener estadísticas: {e}")
        return {
            'total_miembros': 0,
            'prestamos_activos': 0, 
            'reuniones_mes': 0,
            'total_aportes': 0.0
        }

# FUNCIÓN PARA VERIFICAR LOGIN REAL
def verificar_login_real(correo, contrasena):
    """Verifica credenciales contra la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Buscar usuario por correo
            cursor.execute("""
                SELECT m.id_miembro, m.nombre, m.correo, m.contrasena, r.tipo_rol, m.id_grupo
                FROM miembrogapc m
                JOIN rol r ON m.id_rol = r.id_rol
                WHERE m.correo = %s AND m.contrasena IS NOT NULL
            """, (correo,))
            
            usuario = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if usuario:
                # Verificar contraseña
                if usuario['contrasena'] == contrasena:
                    return {
                        'id': usuario['id_miembro'],
                        'nombre': usuario['nombre'],
                        'correo': usuario['correo'],
                        'tipo_rol': usuario['tipo_rol'],
                        'id_grupo': usuario['id_grupo']
                    }
        
        return None
        
    except Exception as e:
        st.error(f"Error al verificar login: {e}")
        return None

# FUNCIÓN DE LOGIN MEJORADA
def mostrar_formulario_login():
    """Muestra el formulario de login con opción de modo prueba/real"""
    
    st.markdown('<div class="main-header">🏠 Sistema GAPC</div>', unsafe_allow_html=True)
    
    # Probar conexión primero
    if st.button("🔍 Probar Conexión a Base de Datos"):
        conexion = obtener_conexion()
        if conexion:
            st.success("✅ ¡Conexión exitosa a Clever Cloud!")
            conexion.close()
        else:
            st.error("❌ No se pudo conectar a la base de datos")
    
    # Selector de modo
    modo = st.radio(
        "Selecciona modo de acceso:",
        ["🧪 Modo Prueba", "🔐 Modo Real"],
        horizontal=True
    )
    
    st.markdown("""
        <div class="login-container">
    """, unsafe_allow_html=True)
    
    st.subheader("🔐 Iniciar Sesión")
    
    with st.form("login_form"):
        if modo == "🔐 Modo Real":
            correo = st.text_input("📧 Correo Electrónico", placeholder="usuario@ejemplo.com")
        else:
            correo = st.text_input("👤 Nombre de Usuario", placeholder="Ingresa cualquier nombre")
            
        contrasena = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••")
        
        submitted = st.form_submit_button("🚀 Ingresar al Sistema", use_container_width=True)
        
        if submitted:
            if correo and contrasena:
                with st.spinner("Verificando credenciales..."):
                    if modo == "🔐 Modo Real":
                        # Login real contra base de datos
                        usuario = verificar_login_real(correo, contrasena)
                        if usuario:
                            st.session_state.usuario = usuario
                            st.success(f"¡Bienvenido/a {usuario['nombre']}! 👋")
                            st.rerun()
                        else:
                            st.error("❌ Credenciales incorrectas o usuario no existe")
                    else:
                        # Modo prueba - acepta cualquier cosa
                        st.session_state.usuario = {
                            'nombre': correo.title(),
                            'tipo_rol': 'Usuario',
                            'id_grupo': 1
                        }
                        st.success(f"¡Bienvenido/a {st.session_state.usuario['nombre']}! 👋 (Modo Prueba)")
                        st.rerun()
            else:
                st.warning("⚠️ Por favor completa todos los campos")
    
    # Información según el modo
    with st.expander("💡 Información de acceso"):
        if modo == "🧪 Modo Prueba":
            st.write("""
            **Para desarrollo y pruebas:**
            - 👤 Cualquier nombre de usuario
            - 🔒 Cualquier contraseña
            - ✅ Acceso inmediato
            """)
        else:
            st.write("""
            **Modo de producción:**
            - 📧 Correo registrado en la base de datos
            - 🔒 Contraseña correcta
            - 🔐 Verificación contra usuarios reales
            - 🌐 **Base de datos:** Clever Cloud MySQL
            """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# FUNCIÓN DE DASHBOARD CON MÉTRICAS REALES
def mostrar_dashboard_principal():
    """Muestra el dashboard principal con datos reales"""
    
    usuario = st.session_state.usuario
    
    # Header con mensaje de bienvenida
    st.markdown(f'''
    <div class="welcome-message">
        <h2>👋 ¡Hola, {usuario['nombre']}!</h2>
        <p>Bienvenido/a al Sistema de Gestión GAPC</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/6f42c1/white?text=GAPC", width=150)
        st.markdown("---")
        st.write(f"**👤 Usuario:** {usuario['nombre']}")
        st.write(f"**🎭 Rol:** {usuario['tipo_rol']}")
        st.write(f"**🏢 Grupo:** #{usuario.get('id_grupo', 1)}")
        
        # Mostrar modo actual
        if 'correo' in usuario:
            st.write("**🔐 Modo:** Real")
        else:
            st.write("**🧪 Modo:** Prueba")
            
        st.markdown("---")
        
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()
            
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario = None
            st.rerun()
    
    # MÉTRICAS PRINCIPALES (REALES)
    st.subheader("📊 Resumen General - Datos en Tiempo Real")
    
    # Obtener estadísticas reales
    id_grupo_usuario = usuario.get('id_grupo')
    estadisticas = obtener_estadisticas_reales(id_grupo_usuario)
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👥 Miembros", 
            estadisticas['total_miembros'],
            help="Total de miembros en el sistema"
        )

    with col2:
        st.metric(
            "💰 Préstamos Activos", 
            estadisticas['prestamos_activos'],
            help="Préstamos actualmente aprobados"
        )

    with col3:
        st.metric(
            "📅 Reuniones Mes", 
            estadisticas['reuniones_mes'],
            help="Reuniones realizadas este mes"
        )

    with col4:
        st.metric(
            "💵 Aportes Mes", 
            f"₡{estadisticas['total_aportes']:,.2f}",
            help="Total de aportes este mes"
        )
    
    # Módulos del sistema
    st.subheader("🚀 Módulos del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Gestión de Miembros")
        if st.button("📋 Lista de Miembros", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
        if st.button("➕ Agregar Miembro", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
        
        st.markdown("### 📅 Reuniones")
        if st.button("🗓️ Calendario", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
        if st.button("✅ Asistencia", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
    
    with col2:
        st.markdown("### 💰 Gestión Financiera")
        if st.button("🏦 Préstamos", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
        if st.button("💰 Aportes", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
        
        st.markdown("### 📊 Reportes")
        if st.button("📈 Dashboard", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
        if st.button("📋 Generales", use_container_width=True):
            st.info("🔧 Módulo en desarrollo - Próximamente")
    
    # Información adicional
    st.markdown("---")
    st.subheader("ℹ️ Información del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        conexion_status = "Conectada ✅ (Clever Cloud)" if obtener_conexion() else "Desconectada ❌"
        st.info(f"**Base de datos:** {conexion_status}")
    
    with col2:
        st.info("**Sistema GAPC v1.0**")
        st.info("**Estado:** 🟢 En funcionamiento")

# APLICACIÓN PRINCIPAL
def main():
    """Función principal de la aplicación"""
    
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        mostrar_dashboard_principal()

if __name__ == "__main__":
    main()
