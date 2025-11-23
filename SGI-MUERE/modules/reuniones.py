import streamlit as st
import pymysql
from datetime import datetime
from dateutil.relativedelta import relativedelta
import traceback

# ---------------------------------------------------
# Configuración de conexión
# ---------------------------------------------------
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

# ---------------------------------------------------
# Función de diagnóstico
# ---------------------------------------------------
def probar_conexion_y_tablas():
    """Función para diagnosticar problemas de conexión"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()

            # Probar consulta SELECT
            cursor.execute("SELECT COUNT(*) as total FROM reunion")
            resultado = cursor.fetchone()
            total = resultado['total'] if resultado and 'total' in resultado else 'desconocido'
            st.info(f"✅ Tabla 'reunion' accesible. Registros: {total}")

            # Probar INSERT simple
            cursor.execute("""
                INSERT INTO reunion (id_grupo, fecha, hora, saldo_inicial, saldo_final, acuerdos) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (1, '2024-01-01', '10:00:00', 1000.00, 1200.00, 'Prueba diagnóstico'))

            id_reunion = cursor.lastrowid
            conexion.commit()

            st.success(f"✅ INSERT de prueba exitoso. ID generado: {id_reunion}")

            # Limpiar prueba
            cursor.execute("DELETE FROM reunion WHERE acuerdos = %s", ('Prueba diagnóstico',))
            conexion.commit()

            cursor.close()
            conexion.close()
            return True
        else:
            st.error("❌ No se pudo establecer conexión")
            return False

    except Exception as e:
        st.error(f"❌ Error en diagnóstico: {e}")
        st.error(f"🔍 Detalles: {traceback.format_exc()}")
        return False

# ---------------------------------------------------
# Módulo principal
# ---------------------------------------------------
def mostrar_modulo_reuniones():
    """Módulo de gestión de reuniones"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 📅 Módulo de Reuniones")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Menú de opciones
    opcion = st.radio(
        "Selecciona una acción:",
        ["➕ Nueva Reunión", "📋 Historial de Reuniones"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "➕ Nueva Reunión":
        mostrar_nueva_reunion()
    elif opcion == "📋 Historial de Reuniones":
        mostrar_historial_reuniones()

# ---------------------------------------------------
# Interfaz para nueva reunión (incluye botón diagnóstico)
# ---------------------------------------------------
def mostrar_nueva_reunion():
    """Interfaz para crear una nueva reunión"""
    st.subheader("➕ Nueva Reunión")
    
    # BOTÓN DE DIAGNÓSTICO TEMPORAL
    if st.button("🔧 Ejecutar Diagnóstico de Base de Datos"):
        probar_conexion_y_tablas()
        return

    # Inicializar listas en session_state si no existen
    if 'prestamos_temporales' not in st.session_state:
        st.session_state.prestamos_temporales = []
    if 'aportes_temporales' not in st.session_state:
        st.session_state.aportes_temporales = []
    
    # 1. Datos automáticos
    nombre_grupo, saldo_inicial = obtener_datos_automaticos()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**🏢 Grupo:** {nombre_grupo}")
    with col2:
        st.success(f"**💰 Saldo Inicial:** ${saldo_inicial:,.2f}")
    
    st.markdown("---")
    
    # 2. Datos que el usuario ingresa
    with st.form("form_nueva_reunion"):
        st.subheader("📅 Información de la Reunión")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_reunion = st.date_input("Fecha de la reunión *", value=datetime.now())
        with col2:
            hora_reunion = st.time_input("Hora de la reunión *", value=datetime.now().time())
        
        acuerdos = st.text_area("📝 Acuerdos de la reunión", 
                               placeholder="Ej: Se acordó comprar materiales para...\nTareas asignadas: Juan - llevar acta...")

        st.markdown("---")
        
        # 3. Registro de asistencia
        st.subheader("🧍 Asistencia de Miembros")
        asistencias = registrar_asistencia()
        
        submitted = st.form_submit_button("💾 Guardar Reunión", use_container_width=True)
        # Nota: el guardado completo está fuera del formulario para incluir movimientos
        # si deseas que el formulario guarde todo directamente, mover la lógica aquí.
    
    st.markdown("---")
    
    # 4. Movimientos de la reunión (FUERA del formulario)
    st.subheader("💸 Movimientos de la Reunión")
    
    # 4A. Préstamos - FUERA del formulario
    st.write("**📤 Préstamos Solicitados**")
    prestamos_otorgados = procesar_prestamos(saldo_inicial)
    
    # 4B. Aportes - FUERA del formulario  
    st.write("**📥 Aportes Realizados**")
    aportes_realizados = procesar_aportes()
    
    st.markdown("---")
    
    # 5. Cálculo de saldo final
    saldo_final = calcular_saldo_final(saldo_inicial, prestamos_otorgados, aportes_realizados)
    
    st.success(f"**🧮 Saldo Final Calculado:** ${saldo_final:,.2f}")
    
    # Botón de guardar reunión (ahora fuera del formulario)
    if st.button("💾 Guardar Reunión Completa", type="primary", use_container_width=True):
        if not fecha_reunion or not hora_reunion:
            st.error("❌ Fecha y hora son obligatorios")
        else:
            guardar_reunion_completa(
                fecha_reunion, hora_reunion, acuerdos, asistencias, 
                prestamos_otorgados, aportes_realizados, saldo_inicial, saldo_final
            )
            # Limpiar listas temporales después de guardar
            st.session_state.prestamos_temporales = []
            st.session_state.aportes_temporales = []

# ---------------------------------------------------
# Obtener datos automáticos
# ---------------------------------------------------
def obtener_datos_automaticos():
    """Obtiene nombre del grupo y saldo inicial automáticamente"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener nombre del grupo
            cursor.execute("SELECT nombre_grupo FROM grupo WHERE id_grupo = %s", (id_grupo,))
            grupo = cursor.fetchone()
            nombre_grupo = grupo['nombre_grupo'] if grupo else f"Grupo #{id_grupo}"
            
            # Obtener saldo inicial (suma de todos los aportes hasta ahora)
            cursor.execute("""
                SELECT COALESCE(SUM(a.monto), 0) as saldo 
                FROM aporte a 
                JOIN reunion r ON a.id_reunion = r.id_reunion 
                WHERE r.id_grupo = %s
            """, (id_grupo,))
            
            resultado = cursor.fetchone()
            saldo_inicial = float(resultado['saldo']) if resultado and 'saldo' in resultado else 0.0
            
            cursor.close()
            conexion.close()
            
            return nombre_grupo, saldo_inicial
            
    except Exception as e:
        st.error(f"Error al obtener datos automáticos: {e}")
        st.error(f"🔍 Detalles: {traceback.format_exc()}")
    
    return "Grupo", 0.0

# ---------------------------------------------------
# Registrar asistencia
# ---------------------------------------------------
def registrar_asistencia():
    """Registra la asistencia de miembros y aplica multas automáticamente (solo UI, no guarda aún)"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener miembros del grupo
            cursor.execute("""
                SELECT m.id_miembro, m.nombre 
                FROM miembrogapc m 
                WHERE m.id_grupo = %s 
                ORDER BY m.nombre
            """, (id_grupo,))
            
            miembros = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            asistencias = {}
            st.write("**Marque ✅ los miembros que asistieron:**")
            
            for miembro in miembros:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"👤 {miembro['nombre']}")
                with col2:
                    # Checkbox por miembro
                    key = f"asist_{miembro['id_miembro']}"
                    # Si la key ya existe, conservar valor; si no, predeterminar True
                    value = st.session_state.get(key, True)
                    asistio = st.checkbox("Asistió", value=value, key=key)
                    asistencias[miembro['id_miembro']] = asistio
            
            return asistencias
            
    except Exception as e:
        st.error(f"Error al cargar miembros para asistencia: {e}")
        st.error(f"🔍 Detalles: {traceback.format_exc()}")
    
    return {}

# ---------------------------------------------------
# Procesar préstamos (interfaz)
# ---------------------------------------------------
def procesar_prestamos(saldo_inicial):
    """Procesa solicitudes de préstamos durante la reunión - AHORA CON MÚLTIPLES PRÉSTAMOS"""
    
    # Mostrar préstamos ya agregados
    if st.session_state.prestamos_temporales:
        st.write("**📋 Préstamos registrados en esta reunión:**")
        for i, prestamo in enumerate(st.session_state.prestamos_temporales):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"- {prestamo['nombre']}: ${prestamo['monto']:,.2f} ({prestamo['proposito']})")
            with col2:
                st.write(f"Plazo: {prestamo['plazo_meses']} meses")
            with col3:
                if st.button("🗑️", key=f"del_prest_{i}"):
                    st.session_state.prestamos_temporales.pop(i)
                    st.rerun()
    
    # Formulario para agregar NUEVO préstamo
    with st.expander("➕ Agregar Nuevo Préstamo"):
        try:
            conexion = obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                
                id_grupo = st.session_state.usuario.get('id_grupo', 1)
                
                # Obtener miembros con su ahorro actual
                cursor.execute("""
                    SELECT m.id_miembro, m.nombre, COALESCE(SUM(a.monto), 0) as ahorro
                    FROM miembrogapc m
                    LEFT JOIN aporte a ON m.id_miembro = a.id_miembro
                    WHERE m.id_grupo = %s
                    GROUP BY m.id_miembro, m.nombre
                """, (id_grupo,))
                
                miembros = cursor.fetchall()
                cursor.close()
                conexion.close()
                
                if miembros:
                    # Selector de miembro
                    opciones_miembros = [f"{m['id_miembro']} - {m['nombre']} (Ahorro: ${m['ahorro']:,.2f})" for m in miembros]
                    miembro_seleccionado = st.selectbox(
                        "👤 Miembro solicitante:",
                        opciones_miembros,
                        key="prestamo_miembro"
                    )
                    
                    monto_prestamo = st.number_input("💵 Monto del préstamo:", min_value=0.0, step=100.0, key="monto_prestamo")
                    proposito = st.text_input("📋 Propósito del préstamo:", placeholder="Ej: Compra de materiales, Emergencia médica...")
                    plazo_meses = st.number_input("📅 Plazo en meses:", min_value=1, max_value=24, value=6, key="plazo_prestamo")
                    
                    if st.button("✅ Agregar Préstamo a la Reunión", key="agregar_prestamo"):
                        if miembro_seleccionado and monto_prestamo > 0:
                            miembro_id = int(miembro_seleccionado.split(" - ")[0])
                            miembro_nombre = next(m['nombre'] for m in miembros if m['id_miembro'] == miembro_id)
                            ahorro_miembro = next(m['ahorro'] for m in miembros if m['id_miembro'] == miembro_id)
                            
                            # Validaciones
                            if monto_prestamo > ahorro_miembro:
                                st.error(f"❌ Préstamo DENEGADO: El monto (${monto_prestamo:,.2f}) supera el ahorro disponible (${ahorro_miembro:,.2f})")
                            elif monto_prestamo > saldo_inicial:
                                st.error(f"❌ Préstamo DENEGADO: El monto supera el saldo disponible del grupo (${saldo_inicial:,.2f})")
                            else:
                                prestamo = {
                                    'id_miembro': miembro_id,
                                    'nombre': miembro_nombre,
                                    'monto': monto_prestamo,
                                    'proposito': proposito,
                                    'plazo_meses': plazo_meses,
                                    'estado': 'aprobado'
                                }
                                st.session_state.prestamos_temporales.append(prestamo)
                                st.success(f"✅ Préstamo agregado para {miembro_nombre} por ${monto_prestamo:,.2f}")
                                st.rerun()
                        else:
                            st.warning("⚠️ Completa todos los campos del préstamo")
                else:
                    st.info("📝 No hay miembros en el grupo para asignar préstamos")
                    
        except Exception as e:
            st.error(f"Error al procesar préstamos: {e}")
            st.error(f"🔍 Detalles: {traceback.format_exc()}")
    
    return st.session_state.prestamos_temporales

# ---------------------------------------------------
# Procesar aportes (interfaz)
# ---------------------------------------------------
def procesar_aportes():
    """Procesa los aportes durante la reunión - AHORA CON MÚLTIPLES APORTES"""
    
    # Mostrar aportes ya agregados
    if st.session_state.aportes_temporales:
        st.write("**📋 Aportes registrados en esta reunión:**")
        for i, aporte in enumerate(st.session_state.aportes_temporales):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"- {aporte['nombre']}: ${aporte['monto']:,.2f}")
            with col2:
                st.write(f"Tipo: {aporte['tipo']}")
            with col3:
                if st.button("🗑️", key=f"del_aport_{i}"):
                    st.session_state.aportes_temporales.pop(i)
                    st.rerun()
    
    # Formulario para agregar NUEVO aporte
    with st.expander("💰 Registrar Nuevo Aporte"):
        try:
            conexion = obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                
                id_grupo = st.session_state.usuario.get('id_grupo', 1)
                
                # Obtener miembros del grupo
                cursor.execute("SELECT id_miembro, nombre FROM miembrogapc WHERE id_grupo = %s ORDER BY nombre", (id_grupo,))
                miembros = cursor.fetchall()
                cursor.close()
                conexion.close()
                
                if miembros:
                    miembro_aporte = st.selectbox(
                        "👤 Miembro que aporta:",
                        [f"{m['id_miembro']} - {m['nombre']}" for m in miembros],
                        key="aporte_miembro"
                    )
                    
                    tipo_aporte = st.selectbox(
                        "📋 Tipo de aporte:",
                        ['Ahorro', 'Rifa', 'Pago de préstamo', 'Pago de multa', 'Otros'],
                        key="tipo_aporte"
                    )
                    
                    monto_aporte = st.number_input("💵 Monto del aporte:", min_value=0.0, step=10.0, key="monto_aporte")
                    
                    if st.button("➕ Agregar Aporte a la Reunión", key="agregar_aporte"):
                        if miembro_aporte and monto_aporte > 0:
                            miembro_id = int(miembro_aporte.split(" - ")[0])
                            miembro_nombre = next(m['nombre'] for m in miembros if m['id_miembro'] == miembro_id)
                            
                            aporte = {
                                'id_miembro': miembro_id,
                                'nombre': miembro_nombre,
                                'monto': monto_aporte,
                                'tipo': tipo_aporte
                            }
                            st.session_state.aportes_temporales.append(aporte)
                            st.success(f"✅ Aporte de {miembro_nombre} registrado: ${monto_aporte:,.2f} - {tipo_aporte}")
                            st.rerun()
                        else:
                            st.warning("⚠️ Completa todos los campos del aporte")
                else:
                    st.info("📝 No hay miembros en el grupo para registrar aportes")
    
        except Exception as e:
            st.error(f"Error al procesar aportes: {e}")
            st.error(f"🔍 Detalles: {traceback.format_exc()}")
    
    return st.session_state.aportes_temporales

# ---------------------------------------------------
# Calcular saldo final
# ---------------------------------------------------
def calcular_saldo_final(saldo_inicial, prestamos, aportes):
    """Calcula el saldo final automáticamente"""
    total_prestamos = sum(p['monto'] for p in prestamos)
    total_aportes = sum(a['monto'] for a in aportes)
    
    saldo_final = saldo_inicial + total_aportes - total_prestamos
    return saldo_final

# ---------------------------------------------------
# Guardar reunión completa (con manejo detallado de errores)
# ---------------------------------------------------
def guardar_reunion_completa(fecha, hora, acuerdos, asistencias, prestamos, aportes, saldo_inicial, saldo_final):
    """Guarda toda la información de la reunión en la base de datos"""
    try:
        conexion = obtener_conexion()
        if not conexion:
            st.error("❌ No se pudo conectar a la base de datos para guardar la reunión.")
            return

        cursor = conexion.cursor()
        id_grupo = st.session_state.usuario.get('id_grupo', 1)

        st.info(f"🔍 Intentando guardar reunión para grupo: {id_grupo}")

        # 1. Insertar la reunión
        cursor.execute("""
            INSERT INTO reunion (id_grupo, fecha, hora, saldo_inicial, saldo_final, acuerdos)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_grupo, fecha, hora, saldo_inicial, saldo_final, acuerdos))

        id_reunion = cursor.lastrowid
        st.info(f"🔍 Reunión insertada. ID: {id_reunion}")

        # 2. Guardar asistencias y aplicar multas automáticamente
        monto_multa = 5.00

        for id_miembro, asistio in asistencias.items():
            cursor.execute("""
                INSERT INTO asistencia (id_reunion, id_miembro, estado, multa_aplicada)
                VALUES (%s, %s, %s, %s)
            """, (id_reunion, id_miembro, 'presente' if asistio else 'ausente', 0.0 if asistio else monto_multa))

            if not asistio:
                cursor.execute("""
                    INSERT INTO multa (id_miembro, motivo, monto, id_estado)
                    VALUES (%s, %s, %s, %s)
                """, (id_miembro, f"Falta a reunión {fecha}", monto_multa, 1))  # id_estado 1 = activo

        st.info(f"🔍 Asistencias guardadas: {len(asistencias)} miembros")

        # 3. Guardar préstamos aprobados
        for prestamo in prestamos:
            fecha_vencimiento = datetime.now().date() + relativedelta(months=prestamo['plazo_meses'])

            cursor.execute("""
                INSERT INTO prestamo (id_miembro, id_reunion, monto_prestado, proposito, fecha_vencimiento, plazo_meses, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (prestamo['id_miembro'], id_reunion, prestamo['monto'], prestamo.get('proposito', ''), 
                  fecha_vencimiento, prestamo['plazo_meses'], prestamo.get('estado', 'aprobado')))

        st.info(f"🔍 Préstamos guardados: {len(prestamos)}")

        # 4. Guardar aportes
        for aporte in aportes:
            tipo_bd = aporte['tipo']
            if aporte['tipo'] == 'Pago de préstamo':
                tipo_bd = 'PagoPrestamo'
            elif aporte['tipo'] == 'Pago de multa':
                tipo_bd = 'PagoMulta'

            cursor.execute("""
                INSERT INTO aporte (id_reunion, id_miembro, monto, tipo)
                VALUES (%s, %s, %s, %s)
            """, (id_reunion, aporte['id_miembro'], aporte['monto'], tipo_bd))

        st.info(f"🔍 Aportes guardados: {len(aportes)}")

        # Hacer commit de TODOS los cambios
        conexion.commit()
        cursor.close()
        conexion.close()

        st.success("🎉 ¡Reunión guardada exitosamente!")
        st.balloons()

    except Exception as e:
        st.error(f"❌ Error al guardar la reunión: {str(e)}")
        st.error(f"🔍 Detalles del error: {traceback.format_exc()}")

# ---------------------------------------------------
# Mostrar historial de reuniones
# ---------------------------------------------------
def mostrar_historial_reuniones():
    """Muestra el historial de reuniones anteriores"""
    st.subheader("📋 Historial de Reuniones")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            cursor.execute("""
                SELECT r.id_reunion, r.fecha, r.hora, r.saldo_inicial, r.saldo_final, r.acuerdos,
                       COUNT(a.id_asistencia) as total_asistentes
                FROM reunion r
                LEFT JOIN asistencia a ON r.id_reunion = a.id_reunion AND a.estado = 'presente'
                WHERE r.id_grupo = %s
                GROUP BY r.id_reunion, r.fecha, r.hora, r.saldo_inicial, r.saldo_final, r.acuerdos
                ORDER BY r.fecha DESC
            """, (id_grupo,))
            
            reuniones = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if reuniones:
                for reunion in reuniones:
                    with st.expander(f"📅 Reunión del {reunion['fecha']} - {reunion['hora']}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**💰 Saldo Inicial:** ${reunion['saldo_inicial']:,.2f}")
                            st.write(f"**🧮 Saldo Final:** ${reunion['saldo_final']:,.2f}")
                            st.write(f"**👥 Asistentes:** {reunion['total_asistentes']}")
                        with col2:
                            if reunion['acuerdos']:
                                st.write("**📝 Acuerdos:**")
                                st.write(reunion['acuerdos'])
            else:
                st.info("📝 No hay reuniones registradas para este grupo.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar historial: {e}")
        st.error(f"🔍 Detalles: {traceback.format_exc()}")

