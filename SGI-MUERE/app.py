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
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    .saldo-card {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .module-button {
        background: white;
        color: #6f42c1;
        border: 2px solid #6f42c1;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem;
        font-weight: bold;
        font-size: 1.1rem;
        width: 100%;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .module-button:hover {
        background: #6f42c1;
        color: white;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Función de conexión a BD - CLEVER CLOUD
def obtener_conexion():
    try:
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
            
            # Total de aportes (SALDO ACTUAL)
            if id_grupo:
                cursor.execute("""
                    SELECT COALESCE(SUM(a.monto), 0) as total 
                    FROM aporte a
                    JOIN reunion r ON a.id_reunion = r.id_reunion
                    WHERE r.id_gruppo = %s
                """, (id_grupo,))
            else:
                cursor.execute("""
                    SELECT COALESCE(SUM(a.monto), 0) as total 
                    FROM aporte a
                    JOIN reunion r ON a.id_reunion = r.id_reunion
                """)
            resultado = cursor.fetchone()
            estadisticas['saldo_actual'] = float(resultado['total']) if resultado and resultado['total'] else 0.0
            
            cursor.close()
            conexion.close()
            return estadisticas
            
    except Exception as e:
        st.error(f"Error al obtener estadísticas: {e}")
        return {
            'total_miembros': 0,
            'prestamos_activos': 0, 
            'reuniones_mes': 0,
            'saldo_actual': 0.0
        }

# FUNCIÓN PARA VERIFICAR LOGIN REAL
def verificar_login_real(correo, contrasena):
    """Verifica credenciales contra la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
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

# FUNCIÓN DE LOGIN
def mostrar_formulario_login():
    """Muestra el formulario de login"""
    
    st.markdown('<div class="main-header">🏠 Sistema GAPC</div>', unsafe_allow_html=True)
    
    # Probar conexión primero
    if st.button("🔍 Probar Conexión a Base de Datos"):
        conexion = obtener_conexion()
        if conexion:
            st.success("✅ ¡Conexión exitosa a Clever Cloud!")
            conexion.close()
        else:
            st.error("❌ No se pudo conectar a la base de datos")
    
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
                        usuario = verificar_login_real(correo, contrasena)
                        if usuario:
                            st.session_state.usuario = usuario
                            st.success(f"¡Bienvenido/a {usuario['nombre']}! 👋")
                            st.rerun()
                        else:
                            st.error("❌ Credenciales incorrectas o usuario no existe")
                    else:
                        st.session_state.usuario = {
                            'nombre': correo.title(),
                            'tipo_rol': 'Usuario',
                            'id_grupo': 1
                        }
                        st.success(f"¡Bienvenido/a {st.session_state.usuario['nombre']}! 👋 (Modo Prueba)")
                        st.rerun()
            else:
                st.warning("⚠️ Por favor completa todos los campos")
    
    st.markdown("</div>", unsafe_allow_html=True)

# FUNCIÓN DE DASHBOARD CON NUEVO DISEÑO
def mostrar_dashboard_principal():
    """Muestra el dashboard principal con el nuevo diseño"""
    
    usuario = st.session_state.usuario
    
    # Obtener estadísticas reales
    id_grupo_usuario = usuario.get('id_grupo')
    estadisticas = obtener_estadisticas_reales(id_grupo_usuario)
    
    # SIDEBAR
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/6f42c1/white?text=GAPC", width=150)
        st.markdown("---")
        st.write(f"**👤 Usuario:** {usuario['nombre']}")
        st.write(f"**🎭 Rol:** {usuario['tipo_rol']}")
        st.write(f"**🏢 Grupo:** #{usuario.get('id_grupo', 1)}")
        
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
    
    # CONTENIDO PRINCIPAL
    # Header de bienvenida
    st.markdown(f'''
    <div class="welcome-message">
        <h1>¡Bienvenido/a, {usuario['nombre']}!</h1>
        <h3>{usuario['tipo_rol']} - Grupo #{usuario.get('id_grupo', 1)}</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # SALDO ACTUAL (ÚNICA MÉTRICA)
    st.markdown("## 💰 Resumen Financiero")
    
    st.markdown(f'''
    <div class="saldo-card">
        <h2>SALDO ACTUAL DEL GRUPO</h2>
        <h1>₡{estadisticas['saldo_actual']:,.2f}</h1>
        <p>Total acumulado de aportes</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # BOTONES DE MÓDULOS
    st.markdown("## 🚀 Módulos del Sistema")
    
    # Primera fila de botones
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 **Información de Grupo**", use_container_width=True, key="grupo"):
            st.info("🔧 Módulo Información de Grupo - En desarrollo")
    
    with col2:
        if st.button("👥 **Miembros**", use_container_width=True, key="miembros"):
            st.info("🔧 Módulo Miembros - En desarrollo")
    
    with col3:
        if st.button("📅 **Reunión**", use_container_width=True, key="reunion"):
            st.info("🔧 Módulo Reunión - En desarrollo")
    
    with col4:
        if st.button("💰 **Aportes**", use_container_width=True, key="aportes"):
            st.info("🔧 Módulo Aportes - En desarrollo")
    
    # Segunda fila de botones
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏦 **Préstamos**", use_container_width=True, key="prestamos"):
            st.info("🔧 Módulo Préstamos - En desarrollo")
    
    with col2:
        if st.button("⚖️ **Multa**", use_container_width=True, key="multa"):
            st.info("🔧 Módulo Multa - En desarrollo")
    
    with col3:
        if st.button("📊 **Reporte**", use_container_width=True, key="reporte"):
            st.info("🔧 Módulo Reporte - En desarrollo")
    
    with col4:
        if st.button("🔄 **Cierre**", use_container_width=True, key="cierre"):
            st.info("🔧 Módulo Cierre - En desarrollo")
    
    # Último botón centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚙️ **Configuración**", use_container_width=True, key="configuracion"):
            st.info("🔧 Módulo Configuración - En desarrollo")
    
    # Información del sistema
    st.markdown("---")
    st.markdown(f"*Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")
    
    # Información de conexión (oculta pero disponible)
    with st.expander("🔧 Información Técnica"):
        col1, col2 = st.columns(2)
        with col1:
            conexion_status = "Conectada ✅ (Clever Cloud)" if obtener_conexion() else "Desconectada ❌"
            st.info(f"**Base de datos:** {conexion_status}")
        with col2:
            st.info("**Sistema GAPC v1.0**")

# APLICACIÓN PRINCIPAL
def main():
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        mostrar_dashboard_principal()

if __name__ == "__main__":
    main()
