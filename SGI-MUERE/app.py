import streamlit as st
from modules.auth.login import verificar_login_real
from modules.dashboard.main import mostrar_dashboard_principal
from modules.miembrogapc.miembro import mostrar_modulo_miembros
from modules.reunion.reunion import mostrar_modulo_reuniones
from modules.aportes.aporte import mostrar_modulo_aportes
from modules.prestamo.prestamo import mostrar_modulo_prestamos
from modules.multa.multa import mostrar_modulo_multas
from modules.cierre.cierre import mostrar_modulo_cierre
from modules.grupo.grupo import mostrar_modulo_grupo
from config.conexion import obtener_conexion  # Importar la función de conexión

# Configuración de la página
st.set_page_config(
    page_title="Sistema GAPC",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        color: #6f42c1;
        text-align: center;
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
    }
    .stButton button {
        background-color: #6f42c1;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .login-container {
        max-width: 300px;
        margin: 1rem auto;
        padding: 1rem;
        border: 1px solid #e0d1f9;
        border-radius: 0.5rem;
        background: #f8fafc;
    }
    .status-conexion {
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    .conexion-exitosa {
        background-color: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .conexion-fallida {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'id_grupo' not in st.session_state:
    st.session_state.id_grupo = None
if 'current_module' not in st.session_state:
    st.session_state.current_module = None

# Función para verificar estado de conexión
def verificar_conexion_bd():
    """Verifica el estado de conexión a la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            # Probar una consulta simple
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 as test")
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            return True, "✅ Conectado a Clever Cloud - Base de datos operativa"
        else:
            return False, "❌ No se pudo establecer conexión"
    except Exception as e:
        return False, f"❌ Error de conexión: {str(e)}"

# Función de login
def mostrar_formulario_login():
    """Muestra el formulario de login"""
    
    # VERIFICACIÓN DE CONEXIÓN EN TIEMPO REAL
    st.markdown('<div class="main-header">🏠 Sistema GAPC</div>', unsafe_allow_html=True)
    
    # Mostrar estado de conexión
    conexion_ok, mensaje_conexion = verificar_conexion_bd()
    
    if conexion_ok:
        st.markdown(f'<div class="status-conexion conexion-exitosa">{mensaje_conexion}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-conexion conexion-fallida">{mensaje_conexion}</div>', unsafe_allow_html=True)
        
        # Información adicional para debugging
        with st.expander("🔧 Información para solución de problemas"):
            st.write("**Problema común:** La base de datos en Clever Cloud no tiene las tablas creadas")
            st.write("**Solución:**")
            st.write("1. Ve a tu panel de Clever Cloud")
            st.write("2. Abre la base de datos 'bhzcn4gxgbe5tcxihqd1'")
            st.write("3. Ejecuta el SQL de creación de tablas")
            st.write("4. Inserta datos de prueba (especialmente usuarios)")
            
            if st.button("🔄 Reintentar conexión"):
                st.rerun()
    
    modo = st.radio(
        "Selecciona modo de acceso:",
        ["🧪 Modo Prueba", "🔐 Modo Real"],
        horizontal=True
    )
    
    st.markdown("""<div class="login-container">""", unsafe_allow_html=True)
    
    with st.form("login_form"):
        if modo == "🔐 Modo Real":
            correo = st.text_input("📧 Correo Electrónico", placeholder="usuario@ejemplo.com")
            st.caption("Usa: test@email.com / password123 (si existen datos)")
        else:
            correo = st.text_input("👤 Nombre de Usuario", placeholder="Ingresa cualquier nombre")
            
        contrasena = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••")
        
        # Información sobre modos
        with st.expander("💡 Información de modos"):
            if modo == "🔐 Modo Real":
                st.write("**Modo Real:** Conecta con la base de datos real")
                st.write("• Requiere credenciales válidas en la BD")
                st.write("• Necesita tablas y datos existentes")
                st.write("• Acceso completo al sistema")
            else:
                st.write("**Modo Prueba:** Simula un usuario sin BD")
                st.write("• Funciona sin conexión a base de datos")
                st.write("• Perfecto para desarrollo y pruebas")
                st.write("• Datos de demostración")
        
        submitted = st.form_submit_button("🚀 Ingresar al Sistema", use_container_width=True)
        
        if submitted:
            if correo and contrasena:
                with st.spinner("Verificando credenciales..."):
                    if modo == "🔐 Modo Real":
                        if not conexion_ok:
                            st.error("⚠️ No se puede verificar credenciales - Sin conexión a BD")
                        else:
                            usuario = verificar_login_real(correo, contrasena)
                            if usuario:
                                st.session_state.usuario = usuario
                                st.success(f"¡Bienvenido/a {usuario['nombre']}! 👋")
                                st.rerun()
                            else:
                                st.error("❌ Credenciales incorrectas o usuario no existe")
                                st.info("💡 Asegúrate de que existan usuarios en la base de datos")
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

# APLICACIÓN PRINCIPAL
def main():
    if not st.session_state.usuario:
        mostrar_formulario_login()
    else:
        # Navegación entre módulos
        modulo_actual = st.session_state.current_module
        
        # Mostrar estado de conexión en el sidebar cuando esté logueado
        with st.sidebar:
            conexion_ok, mensaje_conexion = verificar_conexion_bd()
            if conexion_ok:
                st.success("🟢 BD Conectada")
            else:
                st.error("🔴 BD Desconectada")
        
        if modulo_actual == "miembros":
            mostrar_modulo_miembros()
        elif modulo_actual == "reuniones":
            mostrar_modulo_reuniones()
        elif modulo_actual == "aportes":
            mostrar_modulo_aportes()
        elif modulo_actual == "prestamos":
            mostrar_modulo_prestamos()
        elif modulo_actual == "multas":
            mostrar_modulo_multas()
        elif modulo_actual == "cierre":
            mostrar_modulo_cierre()
        elif modulo_actual == "grupo":
            mostrar_modulo_grupo()
        else:
            mostrar_dashboard_principal()

if __name__ == "__main__":
    main()
