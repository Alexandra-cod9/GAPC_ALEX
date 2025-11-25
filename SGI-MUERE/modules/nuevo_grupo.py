import streamlit as st
import pymysql
from datetime import datetime

def obtener_conexion():
    """Función para obtener conexión a la base de datos"""
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

def mostrar_formulario_nuevo_grupo():
    """Formulario completo para crear un nuevo grupo GAPC"""
    
    # Header
    st.markdown("# ➕ Crear Nuevo Grupo GAPC")
    st.markdown("---")
    
    # Obtener el distrito de la promotora
    distrito_promotora = obtener_distrito_promotora()
    
    if not distrito_promotora:
        st.error("❌ No se pudo obtener tu distrito asignado. Contacta al administrador.")
        return
    
    st.info(f"""
    **📍 Tu distrito asignado:**
    - **Distrito:** {distrito_promotora['nombre_distrito']}
    - **Municipio:** {distrito_promotora['nombre_municipio']}
    - **Departamento:** {distrito_promotora['nombre_departamento']}
    
    El nuevo grupo se creará en este distrito.
    """)
    
    st.markdown("---")
    
    # Formulario de creación del grupo
    with st.form("form_nuevo_grupo"):
        st.subheader("📋 Paso 1: Información del Grupo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_grupo = st.text_input(
                "🏷️ Nombre del Grupo *",
                placeholder="Ej: Grupo Esperanza, Las Mariposas...",
                help="Nombre único para identificar al grupo"
            )
            
            nombre_comunidad = st.text_input(
                "🏘️ Nombre de la Comunidad *",
                placeholder="Ej: Comunidad San José, Colonia Las Flores...",
                help="Nombre del lugar donde opera el grupo"
            )
            
            fecha_formacion = st.date_input(
                "📅 Fecha de Formación *",
                value=datetime.now(),
                help="Fecha oficial de formación del grupo"
            )
        
        with col2:
            frecuencia_reuniones = st.selectbox(
                "🔄 Frecuencia de Reuniones *",
                ["semanal", "quincenal", "mensual"],
                help="Con qué frecuencia se reunirá el grupo"
            )
            
            tasa_interes_mensual = st.number_input(
                "💰 Tasa de Interés Mensual (%) *",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                help="Tasa de interés mensual para préstamos"
            )
            
            metodo_reparto_utilidades = st.selectbox(
                "📊 Método de Reparto de Utilidades *",
                ["proporcional", "equitativo"],
                help="Cómo se repartirán las utilidades"
            )
        
        meta_social = st.text_area(
            "🎯 Meta Social del Grupo",
            placeholder="Describe el objetivo o meta social del grupo...",
            help="Propósito o meta que el grupo quiere alcanzar",
            height=100
        )
        
        st.markdown("---")
        st.subheader("📜 Paso 2: Reglamento del Grupo")
        
        texto_reglamento = st.text_area(
            "📋 Texto del Reglamento",
            placeholder="Escribe las reglas y normas del grupo...",
            height=150,
            help="Reglamento interno del grupo"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_multa = st.text_area(
                "⚠️ Tipos de Multas",
                placeholder="Falta a reunión: $5.00\nLlegar tarde: $2.00",
                height=100,
                help="Define los tipos y montos de multas"
            )
        
        with col2:
            reglas_prestamo = st.text_area(
                "💳 Reglas de Préstamos",
                placeholder="Máximo 80% del ahorro\nPlazo máximo: 12 meses",
                height=100,
                help="Reglas para otorgar préstamos"
            )
        
        st.markdown("---")
        st.subheader("👤 Paso 3: Presidente del Grupo")
        st.info("**Registra al primer miembro que será el Presidente del grupo**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_presidente = st.text_input(
                "👤 Nombre Completo del Presidente *",
                placeholder="Ej: María García López",
                help="Nombre completo del presidente"
            )
            
            dui_presidente = st.text_input(
                "🪪 DUI del Presidente *",
                placeholder="Ej: 12345678-9",
                max_chars=10,
                help="Documento Único de Identidad (formato: 12345678-9)"
            )
        
        with col2:
            telefono_presidente = st.text_input(
                "📱 Teléfono del Presidente *",
                placeholder="Ej: 7777-7777",
                help="Número de teléfono del presidente"
            )
            
            correo_presidente = st.text_input(
                "📧 Correo Electrónico (Opcional)",
                placeholder="presidente@ejemplo.com",
                help="Correo para acceso al sistema (opcional)"
            )
        
        contrasena_presidente = st.text_input(
            "🔒 Contraseña (Opcional)",
            type="password",
            placeholder="Mínimo 6 caracteres",
            help="Si proporciona correo, debe crear una contraseña"
        )
        
        st.markdown("---")
        
        # Botón de envío
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "✅ Crear Grupo Completo",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            # Validaciones
            errores = []
            
            if not nombre_grupo:
                errores.append("El nombre del grupo es obligatorio")
            if not nombre_comunidad:
                errores.append("El nombre de la comunidad es obligatorio")
            if not nombre_presidente:
                errores.append("El nombre del presidente es obligatorio")
            if not dui_presidente:
                errores.append("El DUI del presidente es obligatorio")
            if not telefono_presidente:
                errores.append("El teléfono del presidente es obligatorio")
            if correo_presidente and not contrasena_presidente:
                errores.append("Si proporciona correo, debe crear una contraseña")
            if contrasena_presidente and len(contrasena_presidente) < 6:
                errores.append("La contraseña debe tener al menos 6 caracteres")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Crear el grupo completo
                resultado = crear_grupo_completo(
                    distrito_promotora['id_distrito'],
                    nombre_grupo,
                    nombre_comunidad,
                    fecha_formacion,
                    frecuencia_reuniones,
                    tasa_interes_mensual,
                    metodo_reparto_utilidades,
                    meta_social,
                    texto_reglamento,
                    tipo_multa,
                    reglas_prestamo,
                    nombre_presidente,
                    dui_presidente,
                    telefono_presidente,
                    correo_presidente,
                    contrasena_presidente
                )
                
                if resultado['exito']:
                    st.success("🎉 ¡Grupo creado exitosamente!")
                    st.balloons()
                    st.info(f"""
                    **✅ Resumen:**
                    - **Grupo creado:** {nombre_grupo}
                    - **ID del Grupo:** {resultado['id_grupo']}
                    - **Presidente:** {nombre_presidente}
                    - **Ubicación:** {distrito_promotora['nombre_distrito']}
                    """)
                    
                    # Botón para volver
                    if st.button("⬅️ Volver al Dashboard"):
                        st.rerun()
                else:
                    st.error(f"❌ Error al crear el grupo: {resultado['mensaje']}")

def obtener_distrito_promotora():
    """Obtiene el distrito asignado a la promotora"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            usuario = st.session_state.usuario
            id_miembro = usuario.get('id_miembro')
            
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
            """, (id_miembro,))
            
            distrito = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            return distrito
    except Exception as e:
        st.error(f"❌ Error al obtener distrito: {e}")
    
    return None

def crear_grupo_completo(id_distrito, nombre_grupo, nombre_comunidad, fecha_formacion,
                        frecuencia_reuniones, tasa_interes, metodo_reparto, meta_social,
                        texto_reglamento, tipo_multa, reglas_prestamo,
                        nombre_presidente, dui_presidente, telefono_presidente,
                        correo_presidente, contrasena_presidente):
    """Crea un grupo completo con su reglamento y presidente"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # 1. Crear el reglamento primero
            cursor.execute("""
                INSERT INTO reglamento (texto_reglamento, tipo_multa, reglas_prestamo)
                VALUES (%s, %s, %s)
            """, (texto_reglamento, tipo_multa, reglas_prestamo))
            
            id_reglamento = cursor.lastrowid
            
            # 2. Crear el grupo
            cursor.execute("""
                INSERT INTO grupo (
                    nombre_grupo, nombre_comunidad, fecha_formacion,
                    frecuencia_reuniones, tasa_interes_mensual,
                    metodo_reparto_utilidades, meta_social,
                    id_distrito, id_reglamento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre_grupo, nombre_comunidad, fecha_formacion,
                  frecuencia_reuniones, tasa_interes, metodo_reparto,
                  meta_social, id_distrito, id_reglamento))
            
            id_grupo = cursor.lastrowid
            
            # 3. Obtener el id_rol de "Presidente"
            cursor.execute("SELECT id_rol FROM rol WHERE tipo_rol = 'Presidente' LIMIT 1")
            rol_presidente = cursor.fetchone()
            
            if not rol_presidente:
                cursor.close()
                conexion.close()
                return {
                    'exito': False,
                    'mensaje': 'No se encontró el rol de Presidente en la base de datos'
                }
            
            id_rol_presidente = rol_presidente['id_rol']
            
            # 4. Crear el miembro presidente
            if correo_presidente and contrasena_presidente:
                # Con credenciales de acceso
                cursor.execute("""
                    INSERT INTO miembrogapc (
                        nombre, telefono, dui, id_grupo, id_rol,
                        correo, contrasena
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nombre_presidente, telefono_presidente, dui_presidente,
                      id_grupo, id_rol_presidente, correo_presidente, contrasena_presidente))
            else:
                # Sin credenciales de acceso
                cursor.execute("""
                    INSERT INTO miembrogapc (
                        nombre, telefono, dui, id_grupo, id_rol
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (nombre_presidente, telefono_presidente, dui_presidente,
                      id_grupo, id_rol_presidente))
            
            id_presidente = cursor.lastrowid
            
            # 5. Actualizar el contador de grupos en el distrito
            cursor.execute("""
                UPDATE distrito 
                SET cantidad_grupos = cantidad_grupos + 1 
                WHERE id_distrito = %s
            """, (id_distrito,))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            return {
                'exito': True,
                'id_grupo': id_grupo,
                'id_presidente': id_presidente,
                'mensaje': 'Grupo creado exitosamente'
            }
            
    except pymysql.err.IntegrityError as e:
        if 'Duplicate entry' in str(e):
            if 'correo' in str(e):
                return {
                    'exito': False,
                    'mensaje': 'El correo electrónico ya está registrado en el sistema'
                }
            elif 'dui' in str(e):
                return {
                    'exito': False,
                    'mensaje': 'El DUI ya está registrado en el sistema'
                }
        return {
            'exito': False,
            'mensaje': f'Error de integridad en la base de datos: {str(e)}'
        }
    except Exception as e:
        return {
            'exito': False,
            'mensaje': f'Error inesperado: {str(e)}'
        }

def validar_dui(dui):
    """Valida el formato del DUI (12345678-9)"""
    import re
    patron = r'^\d{8}-\d{1}$'
    return bool(re.match(patron, dui))

def validar_telefono(telefono):
    """Valida el formato del teléfono salvadoreño"""
    import re
    # Acepta formatos: 7777-7777, 77777777, 2222-2222, 22222222
    patron = r'^[2,6,7]\d{3}-?\d{4}$'
    return bool(re.match(patron, telefono))
