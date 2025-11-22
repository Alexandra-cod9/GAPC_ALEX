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
# FORMULARIO DE LOGIN
# ==========================================
def mostrar_login():
    st.title("🏠 Sistema GAPC")

    correo = st.text_input("📧 Correo")
    contrasena = st.text_input("🔒 Contraseña", type="password")

    if st.button("Ingresar"):
        usuario = verificar_login(correo, contrasena)
        if usuario:
            st.success(f"Bienvenido {usuario['nombre']}!")
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas")


# ==========================================
# DASHBOARD
# ==========================================
def mostrar_dashboard():
    usuario = st.session_state.usuario
    st.sidebar.success(f"Usuario: {usuario['nombre']}")

    stats = obtener_estadisticas(usuario["id_grupo"])

    st.header("📊 Dashboard Principal")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Miembros", stats["total_miembros"])
    col2.metric("Préstamos Activos", stats["prestamos_activos"])
    col3.metric("Reuniones del Mes", stats["reuniones_mes"])
    col4.metric("Saldo Actual ($)", stats["saldo_actual"])

    st.write("Selecciona un módulo desde la barra lateral.")


# ==========================================
# FLUJO PRINCIPAL
# ==========================================
if st.session_state.usuario is None:
    mostrar_login()
else:
    mostrar_dashboard()
