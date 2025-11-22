# app.py
import streamlit as st
from config.conexion import obtener_conexion
from config.queries import *
from utils.helpers import *

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión - GAPC",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .menu-button {
        width: 100%;
        height: 80px;
        font-size: 1.1rem;
        margin: 5px 0;
    }
    .submenu {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal
    st.markdown('<h1 class="main-header">🏦 Sistema de Gestión - GAPC</h1>', unsafe_allow_html=True)
    
    # Inicializar estado de sesión
    if 'modulo_actual' not in st.session_state:
        st.session_state.modulo_actual = None
    if 'submodulo_actual' not in st.session_state:
        st.session_state.submodulo_actual = None
    
    # Sidebar para navegación principal
    with st.sidebar:
        st.header("📋 Menú Principal")
        
        # Botones del menú principal
        modulos = {
            "👥 Miembros": "miembros",
            "📅 Reuniones": "reuniones", 
            "💰 Aportes": "aportes",
            "🏦 Préstamos": "prestamos",
            "⚖️ Multas": "multas",
            "📊 Reportes": "reportes",
            "🔒 Cierre": "cierre",
            "⚙️ Configuraciones": "configuraciones"
        }
        
        for nombre, clave in modulos.items():
            if st.button(nombre, key=f"btn_{clave}", use_container_width=True):
                st.session_state.modulo_actual = clave
                st.session_state.submodulo_actual = None
                st.rerun()
    
    # Contenido principal basado en el módulo seleccionado
    if st.session_state.modulo_actual:
        mostrar_modulo()
    else:
        mostrar_dashboard_principal()

def mostrar_dashboard_principal():
    """Muestra el dashboard principal cuando no hay módulo seleccionado"""
    st.markdown("### 🏠 Dashboard Principal")
    
    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # Total miembros
                cursor.execute("SELECT COUNT(*) as total FROM miembros WHERE estado = 'activo'")
                total_miembros = cursor.fetchone()['total']
                
                # Total aportes del mes
                cursor.execute("""
                    SELECT COALESCE(SUM(monto), 0) as total 
                    FROM aportes 
                    WHERE MONTH(fecha_aporte) = MONTH(CURRENT_DATE())
                """)
                total_aportes = cursor.fetchone()['total']
                
                # Préstamos activos
                cursor.execute("SELECT COUNT(*) as total FROM prestamos WHERE estado = 'activo'")
                prestamos_activos = cursor.fetchone()['total']
                
                # Multas pendientes
                cursor.execute("SELECT COUNT(*) as total FROM multas WHERE estado = 'pendiente'")
                multas_pendientes = cursor.fetchone()['total']
    
    except Exception as e:
        st.error(f"Error al cargar métricas: {e}")
        total_miembros = total_aportes = prestamos_activos = multas_pendientes = 0
    
    with col1:
        st.metric("👥 Miembros Activos", total_miembros)
    with col2:
        st.metric("💰 Aportes del Mes", f"${total_aportes:,.2f}")
    with col3:
        st.metric("🏦 Préstamos Activos", prestamos_activos)
    with col4:
        st.metric("⚖️ Multas Pendientes", multas_pendientes)
    
    # Bienvenida
    st.info("💡 Selecciona un módulo del menú lateral para comenzar a gestionar.")

def mostrar_modulo():
    """Muestra el módulo y submenú seleccionado"""
    modulo = st.session_state.modulo_actual
    
    # Título del módulo
    st.markdown(f"## 📂 Módulo de {modulo.capitalize()}")
    
    # Mostrar submenú específico del módulo
    if modulo == "miembros":
        submenu_miembros()
    elif modulo == "aportes":
        submenu_aportes()
    elif modulo == "prestamos":
        submenu_prestamos()
    elif modulo == "reuniones":
        submenu_reuniones()
    elif modulo == "multas":
        submenu_multas()
    elif modulo == "reportes":
        submenu_reportes()
    elif modulo == "cierre":
        submenu_cierre()
    elif modulo == "configuraciones":
        submenu_configuraciones()

def submenu_miembros():
    """Submenú para el módulo de miembros"""
    st.markdown('<div class="submenu">', unsafe_allow_html=True)
    st.subheader("👥 Gestión de Miembros")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Agregar Miembro", use_container_width=True):
            st.session_state.submodulo_actual = "agregar_miembro"
            st.rerun()
    
    with col2:
        if st.button("🔍 Buscar Miembro", use_container_width=True):
            st.session_state.submodulo_actual = "buscar_miembro"
            st.rerun()
    
    with col3:
        if st.button("📋 Ver Todos", use_container_width=True):
            st.session_state.submodulo_actual = "ver_todos"
            st.rerun()
    
    with col4:
        if st.button("📊 Estadísticas", use_container_width=True):
            st.session_state.submodulo_actual = "estadisticas"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar contenido del submodulo seleccionado
    if st.session_state.submodulo_actual == "agregar_miembro":
        agregar_miembro()
    elif st.session_state.submodulo_actual == "buscar_miembro":
        buscar_miembro()
    elif st.session_state.submodulo_actual == "ver_todos":
        ver_todos_miembros()
    elif st.session_state.submodulo_actual == "estadisticas":
        mostrar_estadisticas_miembros()

def agregar_miembro():
    """Formulario para agregar nuevo miembro"""
    st.subheader("➕ Agregar Nuevo Miembro")
    
    with st.form("form_agregar_miembro"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo *")
            cedula = st.text_input("Cédula *")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
        
        with col2:
            direccion = st.text_area("Dirección")
            fecha_ingreso = st.date_input("Fecha de ingreso *")
            estado = st.selectbox("Estado *", ["activo", "inactivo", "suspendido"])
        
        # Botones del formulario
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 Guardar Miembro", use_container_width=True)
        with col_btn2:
            st.form_submit_button("🗑️ Cancelar", use_container_width=True)
        
        if submitted:
            if nombre and cedula and fecha_ingreso:
                try:
                    with obtener_conexion() as conexion:
                        with conexion.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO miembros (nombre, cedula, telefono, email, direccion, fecha_ingreso, estado)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (nombre, cedula, telefono, email, direccion, fecha_ingreso, estado))
                            conexion.commit()
                            st.success("✅ Miembro agregado exitosamente!")
                            st.session_state.submodulo_actual = None
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar miembro: {e}")
            else:
                st.warning("⚠️ Por favor complete los campos obligatorios (*)")

def buscar_miembro():
    """Búsqueda y visualización de miembro específico"""
    st.subheader("🔍 Buscar Miembro")
    
    col_busq, col_acc = st.columns([3, 1])
    
    with col_busq:
        termino_busqueda = st.text_input("Buscar por nombre o cédula:")
    
    with col_acc:
        st.write("")  # Espacio vertical
        if st.button("🔍 Buscar", use_container_width=True):
            if termino_busqueda:
                buscar_y_mostrar_miembro(termino_busqueda)
            else:
                st.warning("⚠️ Ingrese un término de búsqueda")

def buscar_y_mostrar_miembro(termino):
    """Busca y muestra la información del miembro"""
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # Buscar miembro
                cursor.execute("""
                    SELECT * FROM miembros 
                    WHERE nombre LIKE %s OR cedula LIKE %s 
                    ORDER BY nombre LIMIT 10
                """, (f"%{termino}%", f"%{termino}%"))
                
                miembros = cursor.fetchall()
                
                if miembros:
                    st.success(f"🔍 Se encontraron {len(miembros)} miembros:")
                    
                    for i, miembro in enumerate(miembros):
                        with st.expander(f"👤 {miembro['nombre']} - {miembro['cedula']}", expanded=i==0):
                            mostrar_detalle_miembro_completo(miembro['id'])
                else:
                    st.warning("❌ No se encontraron miembros con ese criterio")
    
    except Exception as e:
        st.error(f"Error en la búsqueda: {e}")

def mostrar_detalle_miembro_completo(miembro_id):
    """Muestra el detalle completo de un miembro"""
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # Información personal
                cursor.execute("SELECT * FROM miembros WHERE id = %s", (miembro_id,))
                miembro = cursor.fetchone()
                
                if miembro:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**📋 Información Personal:**")
                        st.write(f"**Nombre:** {miembro['nombre']}")
                        st.write(f"**Cédula:** {miembro['cedula']}")
                        st.write(f"**Teléfono:** {miembro['telefono'] or 'No registrado'}")
                        st.write(f"**Email:** {miembro['email'] or 'No registrado'}")
                    
                    with col2:
                        st.write(f"**Dirección:** {miembro['direccion'] or 'No registrada'}")
                        st.write(f"**Fecha Ingreso:** {miembro['fecha_ingreso']}")
                        st.write(f"**Estado:** {miembro['estado']}")
                    
                    # Pestañas para diferentes secciones
                    tab1, tab2, tab3, tab4 = st.tabs(["💰 Aportes", "🏦 Préstamos", "⚖️ Multas", "📊 Historial"])
                    
                    with tab1:
                        mostrar_aportes_miembro(cursor, miembro_id)
                    
                    with tab2:
                        mostrar_prestamos_miembro(cursor, miembro_id)
                    
                    with tab3:
                        mostrar_multas_miembro(cursor, miembro_id)
                    
                    with tab4:
                        mostrar_historial_miembro(cursor, miembro_id)
    
    except Exception as e:
        st.error(f"Error al cargar detalle del miembro: {e}")

def mostrar_aportes_miembro(cursor, miembro_id):
    """Muestra los aportes del miembro"""
    cursor.execute("""
        SELECT * FROM aportes 
        WHERE miembro_id = %s 
        ORDER BY fecha_aporte DESC 
        LIMIT 20
    """, (miembro_id,))
    aportes = cursor.fetchall()
    
    if aportes:
        st.write(f"**Últimos 20 aportes:**")
        for aporte in aportes:
            st.write(f"- ${aporte['monto']:,.2f} - {aporte['tipo_aporte']} - {aporte['fecha_aporte']}")
    else:
        st.info("ℹ️ Este miembro no tiene aportes registrados")

def mostrar_prestamos_miembro(cursor, miembro_id):
    """Muestra los préstamos del miembro"""
    cursor.execute("""
        SELECT * FROM prestamos 
        WHERE miembro_id = %s 
        ORDER BY fecha_prestamo DESC
    """, (miembro_id,))
    prestamos = cursor.fetchall()
    
    if prestamos:
        for prestamo in prestamos:
            st.write(f"**Préstamo:** ${prestamo['monto']:,.2f} - {prestamo['estado']} - {prestamo['fecha_prestamo']}")
    else:
        st.info("ℹ️ Este miembro no tiene préstamos registrados")

def mostrar_multas_miembro(cursor, miembro_id):
    """Muestra las multas del miembro"""
    cursor.execute("""
        SELECT * FROM multas 
        WHERE miembro_id = %s 
        ORDER BY fecha_multa DESC
    """, (miembro_id,))
    multas = cursor.fetchall()
    
    if multas:
        for multa in multas:
            st.write(f"**Multa:** ${multa['monto']:,.2f} - {multa['estado']} - {multa['fecha_multa']}")
    else:
        st.info("ℹ️ Este miembro no tiene multas registradas")

def mostrar_historial_miembro(cursor, miembro_id):
    """Muestra el historial completo del miembro"""
    st.write("**Resumen de actividades:**")
    
    # Aquí puedes agregar más consultas para el historial completo
    cursor.execute("""
        SELECT 'Aporte' as tipo, fecha_aporte as fecha, monto 
        FROM aportes WHERE miembro_id = %s
        UNION ALL
        SELECT 'Préstamo' as tipo, fecha_prestamo as fecha, monto 
        FROM prestamos WHERE miembro_id = %s
        UNION ALL  
        SELECT 'Multa' as tipo, fecha_multa as fecha, monto 
        FROM multas WHERE miembro_id = %s
        ORDER BY fecha DESC LIMIT 30
    """, (miembro_id, miembro_id, miembro_id))
    
    historial = cursor.fetchall()
    
    if historial:
        for item in historial:
            st.write(f"- {item['tipo']}: ${item['monto']:,.2f} - {item['fecha']}")
    else:
        st.info("ℹ️ No hay historial de actividades")

def ver_todos_miembros():
    """Muestra todos los miembros en una tabla"""
    st.subheader("📋 Todos los Miembros")
    
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT * FROM miembros ORDER BY nombre")
                miembros = cursor.fetchall()
                
                if miembros:
                    # Convertir a DataFrame para mejor visualización
                    import pandas as pd
                    df = pd.DataFrame(miembros)
                    
                    # Mostrar tabla
                    st.dataframe(df, use_container_width=True)
                    
                    # Estadísticas rápidas
                    st.write(f"**Total de miembros:** {len(miembros)}")
                    activos = len([m for m in miembros if m['estado'] == 'activo'])
                    st.write(f"**Miembros activos:** {activos}")
                    
                else:
                    st.info("ℹ️ No hay miembros registrados en el sistema")
    
    except Exception as e:
        st.error(f"Error al cargar miembros: {e}")

def mostrar_estadisticas_miembros():
    """Muestra estadísticas de miembros"""
    st.subheader("📊 Estadísticas de Miembros")
    
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # Aquí puedes agregar más consultas estadísticas
                cursor.execute("SELECT COUNT(*) as total FROM miembros")
                total = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as activos FROM miembros WHERE estado = 'activo'")
                activos = cursor.fetchone()['activos']
                
                cursor.execute("SELECT COUNT(*) as inactivos FROM miembros WHERE estado = 'inactivo'")
                inactivos = cursor.fetchone()['inactivos']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Miembros", total)
        col2.metric("Miembros Activos", activos)
        col3.metric("Miembros Inactivos", inactivos)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")

# Aquí continuaríamos con las otras funciones de submenú...
def submenu_aportes():
    """Submenú para el módulo de aportes"""
    st.markdown('<div class="submenu">', unsafe_allow_html=True)
    st.subheader("💰 Gestión de Aportes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Registrar Aporte", use_container_width=True):
            st.session_state.submodulo_actual = "registrar_aporte"
            st.rerun()
    
    with col2:
        if st.button("📋 Ver Aportes", use_container_width=True):
            st.session_state.submodulo_actual = "ver_aportes"
            st.rerun()
    
    with col3:
        if st.button("📊 Reporte Aportes", use_container_width=True):
            st.session_state.submodulo_actual = "reporte_aportes"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Aquí irían las funciones específicas de aportes...

# Continuar con los otros submenús de manera similar...

if __name__ == "__main__":
    main()
