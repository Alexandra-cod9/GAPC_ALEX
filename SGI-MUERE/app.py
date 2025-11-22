# app.py (versión simplificada)
import streamlit as st
import pymysql

# Configuración directa de conexión
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

# Estilos
st.set_page_config(page_title="Sistema GAPC", layout="wide")
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1f77b4; text-align: center; }
    .menu-button { width: 100%; height: 80px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🏦 Sistema de Gestión - GAPC</h1>', unsafe_allow_html=True)
    
    # Estado de sesión
    if 'modulo_actual' not in st.session_state:
        st.session_state.modulo_actual = None
    
    # Menú principal
    with st.sidebar:
        st.header("📋 Menú Principal")
        
        modulos = {
            "👥 Miembros": "miembros",
            "💰 Aportes": "aportes",
            "🏦 Préstamos": "prestamos", 
            "⚖️ Multas": "multas",
            "📅 Reuniones": "reuniones",
            "📊 Reportes": "reportes",
            "🔒 Cierre": "cierre"
        }
        
        for nombre, clave in modulos.items():
            if st.button(nombre, key=clave, use_container_width=True):
                st.session_state.modulo_actual = clave
                st.rerun()
    
    # Contenido según módulo
    if st.session_state.modulo_actual == "miembros":
        modulo_miembros()
    elif st.session_state.modulo_actual == "aportes":
        modulo_aportes()
    else:
        mostrar_dashboard()

def mostrar_dashboard():
    st.subheader("🏠 Dashboard Principal")
    
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # Métricas básicas
                cursor.execute("SELECT COUNT(*) as total FROM miembros")
                total_miembros = cursor.fetchone()['total']
                
                cursor.execute("SELECT COALESCE(SUM(monto), 0) as total FROM aportes WHERE MONTH(fecha_aporte) = MONTH(CURRENT_DATE())")
                total_aportes = cursor.fetchone()['total']
        
        col1, col2 = st.columns(2)
        col1.metric("👥 Total Miembros", total_miembros)
        col2.metric("💰 Aportes del Mes", f"${total_aportes:,.2f}")
        
    except Exception as e:
        st.error(f"Error al cargar dashboard: {e}")

def modulo_miembros():
    st.subheader("👥 Gestión de Miembros")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Agregar Miembro", use_container_width=True):
            st.session_state.accion_miembros = "agregar"
    
    with col2:
        if st.button("🔍 Buscar Miembro", use_container_width=True):
            st.session_state.accion_miembros = "buscar"
    
    with col3:
        if st.button("📋 Ver Todos", use_container_width=True):
            st.session_state.accion_miembros = "ver_todos"
    
    # Mostrar contenido según acción
    if hasattr(st.session_state, 'accion_miembros'):
        if st.session_state.accion_miembros == "agregar":
            agregar_miembro()
        elif st.session_state.accion_miembros == "buscar":
            buscar_miembro()
        elif st.session_state.accion_miembros == "ver_todos":
            ver_todos_miembros()

def agregar_miembro():
    st.subheader("➕ Agregar Nuevo Miembro")
    
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo *")
        cedula = st.text_input("Cédula *")
        telefono = st.text_input("Teléfono")
        
        if st.form_submit_button("💾 Guardar Miembro"):
            if nombre and cedula:
                try:
                    with obtener_conexion() as conexion:
                        with conexion.cursor() as cursor:
                            cursor.execute(
                                "INSERT INTO miembros (nombre, cedula, telefono) VALUES (%s, %s, %s)",
                                (nombre, cedula, telefono)
                            )
                            conexion.commit()
                            st.success("✅ Miembro agregado exitosamente!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Complete los campos obligatorios")

def buscar_miembro():
    st.subheader("🔍 Buscar Miembro")
    
    termino = st.text_input("Buscar por nombre o cédula:")
    if st.button("Buscar") and termino:
        try:
            with obtener_conexion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM miembros WHERE nombre LIKE %s OR cedula LIKE %s LIMIT 10",
                        (f"%{termino}%", f"%{termino}%")
                    )
                    resultados = cursor.fetchall()
                    
                    if resultados:
                        for miembro in resultados:
                            st.write(f"**{miembro['nombre']}** - Cédula: {miembro['cedula']} - Tel: {miembro['telefono']}")
                    else:
                        st.info("No se encontraron miembros")
        except Exception as e:
            st.error(f"Error en búsqueda: {e}")

def ver_todos_miembros():
    st.subheader("📋 Todos los Miembros")
    
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT * FROM miembros ORDER BY nombre")
                miembros = cursor.fetchall()
                
                if miembros:
                    for miembro in miembros:
                        st.write(f"- {miembro['nombre']} ({miembro['cedula']}) - {miembro['estado']}")
                else:
                    st.info("No hay miembros registrados")
    except Exception as e:
        st.error(f"Error: {e}")

def modulo_aportes():
    st.subheader("💰 Gestión de Aportes")
    st.info("Módulo de aportes - En desarrollo")

if __name__ == "__main__":
    main()
