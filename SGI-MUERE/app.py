import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime
import os

# =============== IMPORTAR ROUTER DE MÓDULOS ===============
try:
    from config.modules_router import cargar_modulo
except ModuleNotFoundError:
    def cargar_modulo(nombre):
        st.warning(f"⚠️ El módulo '{nombre}' aún no está creado.")
        return None
# ============================================================

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
if 'modulo_actual' not in st.session_state:
    st.session_state.modulo_actual = None

# ====== (todo tu CSS original) ======
st.markdown("""
<style>
    .main-header { color:#6f42c1;text-align:center;margin-bottom:0.5rem;font-size:1.5rem; }
    .stButton button { background-color:#6f42c1;color:white;border:none;padding:0.3rem 0.6rem;border-radius:0.3rem;font-weight:bold;font-size:0.8rem; }
    .login-container { max-width:300px;margin:1rem auto;padding:1rem;border:1px solid #e0d1f9;border-radius:0.5rem;background:#f8fafc; }
    .welcome-message { background:linear-gradient(135deg,#6f42c1,#8b5cf6);color:white;padding:0.8rem;border-radius:0.5rem;text-align:center;margin:0.5rem 0;font-size:0.8rem; }
    .saldo-card { background:linear-gradient(135deg,#059669,#10b981);color:white;padding:1rem;border-radius:0.5rem;text-align:center;margin:0.5rem 0; }
    .module-button { background:white;color:#6f42c1;border:1px solid #6f42c1;padding:0.6rem;border-radius:0.4rem;margin:0.2rem;font-weight:bold;font-size:0.75rem;width:100%;text-align:center;cursor:pointer; }
    .module-button:hover { background:#6f42c1;color:white; }
</style>
""", unsafe_allow_html=True)

# ====== FUNCIÓN DE CONEXIÓN BD ======
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

# ====== ESTADÍSTICAS ======
def obtener_estadisticas_reales(id_grupo=None):
    try:
        conexion = obtener_conexion()
        if not conexion:
            return { 'total_miembros':0, 'prestamos_activos':0, 'reuniones_mes':0, 'saldo_actual':0 }

        cursor = conexion.cursor()
        est = {}

        # Total miembros
        if id_grupo:
            cursor.execute("SELECT COUNT(*) total FROM miembrogapc WHERE id_grupo=%s", (id_grupo,))
        else:
            cursor.execute("SELECT COUNT(*) total FROM miembrogapc")
        est['total_miembros'] = cursor.fetchone()['total']

        # Préstamos activos
        if id_grupo:
            cursor.execute("""
                SELECT COUNT(*) total FROM prestamo p
                JOIN miembrogapc m ON p.id_miembro=m.id_miembro
                WHERE m.id_grupo=%s AND p.estado='aprobado'
            """, (id_grupo,))
        else:
            cursor.execute("SELECT COUNT(*) total FROM prestamo WHERE estado='aprobado'")
        est['prestamos_activos'] = cursor.fetchone()['total']

        # Reuniones del mes
        if id_grupo:
            cursor.execute("""
                SELECT COUNT(*) total FROM reunion
                WHERE id_gruppo=%s AND MONTH(fecha)=MONTH(CURDATE()) AND YEAR(fecha)=YEAR(CURDATE())
            """, (id_grupo,))
        else:
            cursor.execute("""
                SELECT COUNT(*) total FROM reunion
                WHERE MONTH(fecha)=MONTH(CURDATE()) AND YEAR(fecha)=YEAR(CURDATE())
            """)
        est['reuniones_mes'] = cursor.fetchone()['total']

        # Aportes
        if id_grupo:
            cursor.execute("""
                SELECT COALESCE(SUM(a.monto),0) total FROM aporte a
                JOIN reunion r ON a.id_reunion=r.id_reunion
                WHERE r.id_gruppo=%s
            """, (id_grupo,))
        else:
            cursor.execute("SELECT COALESCE(SUM(monto),0) total FROM aporte")
        est['saldo_actual'] = float(cursor.fetchone()['total'])

        return est

    except Exception as e:
        st.error(f"Error al obtener estadísticas: {e}")
        return { 'total_miembros':0, 'prestamos_activos':0, 'reuniones_mes':0, 'saldo_actual':0 }

# ====== LOGIN REAL ======
def verificar_login_real(correo, contrasena):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT m.id_miembro, m.nombre, m.correo, m.contrasena, r.tipo_rol, m.id_grupo
            FROM miembrogapc m
            JOIN rol r ON m.id_rol=r.id_rol
            WHERE m.correo=%s
        """, (correo,))
        u = cursor.fetchone()

        if u and u["contrasena"] == contrasena:
            return u
        return None

    except:
        return None

# ====== FORMULARIO DE LOGIN ======
def mostrar_formulario_login():
    st.markdown('<div class="main-header">🏠 Sistema GAPC</div>', unsafe_allow_html=True)

    modo = st.radio("Modo:", ["🧪 Prueba", "🔐 Real"], horizontal=True)

    with st.form("login"):
        user = st.text_input("Usuario / Correo")
        pwd = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Ingresar")

        if ok:
            if modo == "🔐 Real":
                u = verificar_login_real(user, pwd)
                if u:
                    st.session_state.usuario = u
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
            else:
                st.session_state.usuario = {
                    "nombre": user,
                    "tipo_rol": "Prueba",
                    "id_grupo": 1
                }
                st.rerun()

# ====== DASHBOARD PRINCIPAL ======
def mostrar_dashboard_principal():
    usuario = st.session_state.usuario
    est = obtener_estadisticas_reales(usuario.get("id_grupo"))

    st.sidebar.markdown("### Navegación")
    if st.sidebar.button("🏠 Inicio"):
        st.session_state.modulo_actual = None

    if st.sidebar.button("👥 Miembros"):
        st.session_state.modulo_actual = "miembros"

    if st.sidebar.button("📅 Reuniones"):
        st.session_state.modulo_actual = "reuniones"

    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.usuario = None
        st.rerun()

    st.markdown(f"""
        <div class="welcome-message">
            <h4>¡Bienvenido/a, {usuario['nombre']}!</h4>
            <p>{usuario['tipo_rol']} - Grupo {usuario.get('id_grupo')}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.modulo_actual:
        # --- CARGAR MÓDULO ---
        modulo = cargar_modulo(st.session_state.modulo_actual)
        if modulo:
            modulo.mostrar()
        return

    st.write("### 🧾 Resumen General")
    st.metric("Miembros", est['total_miembros'])
    st.metric("Préstamos activos", est['prestamos_activos'])
    st.metric("Reuniones del mes", est['reuniones_mes'])
    st.metric("Saldo actual", f"${est['saldo_actual']:,.2f}")

# =============== APP PRINCIPAL ===============
if not st.session_state.usuario:
    mostrar_formulario_login()
else:
    mostrar_dashboard_principal()
