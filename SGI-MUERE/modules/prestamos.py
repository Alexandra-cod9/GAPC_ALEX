import streamlit as st
import pymysql
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

def mostrar_modulo_prestamos():
    """Módulo de gestión de préstamos"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 💳 Módulo de Préstamos")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Menú de opciones
    opcion = st.radio(
        "Selecciona una acción:",
        ["⚙️ Configuración del Grupo", "📤 Nuevo Préstamo", "📋 Historial de Préstamos", "📊 Préstamos Activos"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "⚙️ Configuración del Grupo":
        mostrar_configuracion_grupo()
    elif opcion == "📤 Nuevo Préstamo":
        mostrar_nuevo_prestamo()
    elif opcion == "📋 Historial de Préstamos":
        mostrar_historial_prestamos()
    elif opcion == "📊 Préstamos Activos":
        mostrar_prestamos_activos()

def mostrar_configuracion_grupo():
    """Muestra y permite editar la configuración del grupo para préstamos"""
    st.subheader("⚙️ Configuración de Préstamos del Grupo")
    
    # Obtener configuración actual del grupo
    configuracion = obtener_configuracion_grupo()
    
    with st.form("form_configuracion_prestamos"):
        st.info("**Configura los parámetros para los préstamos del grupo:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Tasa de interés mensual por cada $10
            tasa_interes = st.number_input(
                "💰 Interés mensual por cada $10:",
                min_value=0.0,
                max_value=10.0,
                value=float(configuracion['tasa_interes_mensual']),
                step=0.1,
                help="Ej: $1.50 significa $1.50 de interés mensual por cada $10 prestados"
            )
        
        with col2:
            # Porcentaje máximo de préstamo respecto al ahorro
            porcentaje_maximo = st.number_input(
                "📊 % Máximo del ahorro:",
                min_value=10,
                max_value=100,
                value=configuracion['porcentaje_maximo_prestamo'],
                step=5,
                help="Ej: 80% significa que puede pedir hasta el 80% de su ahorro total"
            )
        
        with col3:
            # Plazo máximo en meses
            plazo_maximo = st.number_input(
                "📅 Plazo máximo (meses):",
                min_value=1,
                max_value=36,
                value=configuracion['plazo_maximo_meses'],
                step=1,
                help="Máximo número de meses para pagar un préstamo"
            )
        
        # Checkbox para permitir múltiples préstamos
        permitir_multiples = st.checkbox(
            "✅ Permitir múltiples préstamos por persona",
            value=configuracion['permitir_multiples_prestamos'],
            help="Si está desactivado, una persona solo puede tener un préstamo a la vez"
        )
        
        if st.form_submit_button("💾 Guardar Configuración", use_container_width=True):
            guardar_configuracion_grupo(tasa_interes, porcentaje_maximo, plazo_maximo, permitir_multiples)
            st.success("✅ Configuración guardada exitosamente!")
            st.rerun()
    
    # Mostrar resumen de la configuración
    st.markdown("---")
    st.subheader("📋 Resumen de Configuración Actual")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Interés Mensual", f"${tasa_interes:.2f} por $10")
    
    with col2:
        st.metric("📊 Límite Préstamo", f"{porcentaje_maximo}% del ahorro")
    
    with col3:
        st.metric("📅 Plazo Máximo", f"{plazo_maximo} meses")
    
    with col4:
        estado = "✅ Múltiples" if permitir_multiples else "❌ Único"
        st.metric("🔒 Préstamos", estado)

def obtener_configuracion_grupo():
    """Obtiene la configuración actual del grupo para préstamos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener configuración del grupo
            cursor.execute("""
                SELECT 
                    tasa_interes_mensual,
                    metodo_reparto_utilidades,
                    meta_social
                FROM grupo 
                WHERE id_grupo = %s
            """, (id_grupo,))
            
            grupo = cursor.fetchone()
            
            # Buscar configuración específica de préstamos (podemos usar la tabla reglamento)
            cursor.execute("""
                SELECT reglas_prestamo 
                FROM reglamento 
                WHERE id_reglamento = %s
            """, (1,))  # Asumiendo que hay un reglamento base
            
            reglamento = cursor.fetchone()
            
            cursor.close()
            conexion.close()
            
            # Configuración por defecto
            configuracion = {
                'tasa_interes_mensual': grupo['tasa_interes_mensual'] if grupo and grupo['tasa_interes_mensual'] else 1.50,
                'porcentaje_maximo_prestamo': 80,  # Por defecto 80%
                'plazo_maximo_meses': 12,  # Por defecto 12 meses
                'permitir_multiples_prestamos': False  # Por defecto no permitir múltiples
            }
            
            # Aquí podríamos parsear reglas_prestamo si están en formato JSON
            # Por ahora usamos valores por defecto
            
            return configuracion
            
    except Exception as e:
        st.error(f"❌ Error al obtener configuración: {e}")
    
    # Retorno por defecto
    return {
        'tasa_interes_mensual': 1.50,
        'porcentaje_maximo_prestamo': 80,
        'plazo_maximo_meses': 12,
        'permitir_multiples_prestamos': False
    }

def guardar_configuracion_grupo(tasa_interes, porcentaje_maximo, plazo_maximo, permitir_multiples):
    """Guarda la configuración del grupo para préstamos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Actualizar tasa de interés en la tabla grupo
            cursor.execute("""
                UPDATE grupo 
                SET tasa_interes_mensual = %s 
                WHERE id_grupo = %s
            """, (tasa_interes, id_grupo))
            
            # Aquí podríamos guardar las otras configuraciones en una tabla específica
            # Por ahora las mantenemos en session_state para esta sesión
            if 'configuracion_prestamos' not in st.session_state:
                st.session_state.configuracion_prestamos = {}
            
            st.session_state.configuracion_prestamos = {
                'porcentaje_maximo_prestamo': porcentaje_maximo,
                'plazo_maximo_meses': plazo_maximo,
                'permitir_multiples_prestamos': permitir_multiples
            }
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
    except Exception as e:
        st.error(f"❌ Error al guardar configuración: {e}")

def mostrar_nuevo_prestamo():
    """Interfaz para solicitar un nuevo préstamo"""
    st.subheader("📤 Solicitar Nuevo Préstamo")
    
    # Obtener configuración actual
    configuracion = obtener_configuracion_grupo()
    if 'configuracion_prestamos' in st.session_state:
        configuracion.update(st.session_state.configuracion_prestamos)
    
    # Mostrar reglas actuales
    st.info(f"""
    **📋 Reglas Actuales del Grupo:**
    - 💰 **Interés:** ${configuracion['tasa_interes_mensual']:.2f} mensual por cada $10
    - 📊 **Límite:** Máximo {configuracion['porcentaje_maximo_prestamo']}% de tu ahorro
    - 📅 **Plazo:** Hasta {configuracion['plazo_maximo_meses']} meses
    - 🔒 **Múltiples:** {'Permitidos' if configuracion['permitir_multiples_prestamos'] else 'No permitidos'}
    """)
    
    with st.form("form_nuevo_prestamo"):
        # Buscar miembro
        miembro_seleccionado = buscar_miembro_prestamo(configuracion)
        
        if miembro_seleccionado:
            st.markdown("---")
            
            # Mostrar información del miembro
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**👤 Miembro:** {miembro_seleccionado['nombre']}")
            with col2:
                st.info(f"**💰 Ahorro Actual:** ${miembro_seleccionado['ahorro_actual']:,.2f}")
            with col3:
                maximo_permitido = miembro_seleccionado['ahorro_actual'] * (configuracion['porcentaje_maximo_prestamo'] / 100)
                st.info(f"**📈 Máximo Permitido:** ${maximo_permitido:,.2f}")
            
            # Datos del préstamo
            st.subheader("📝 Datos del Préstamo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                monto_prestamo = st.number_input(
                    "💵 Monto a solicitar:",
                    min_value=0.0,
                    max_value=float(maximo_permitido),
                    value=0.0,
                    step=100.0,
                    help=f"Máximo permitido: ${maximo_permitido:,.2f}"
                )
                
                plazo_meses = st.number_input(
                    "📅 Plazo en meses:",
                    min_value=1,
                    max_value=configuracion['plazo_maximo_meses'],
                    value=min(6, configuracion['plazo_maximo_meses']),
                    step=1,
                    help=f"Máximo: {configuracion['plazo_maximo_meses']} meses"
                )
            
            with col2:
                proposito = st.text_area(
                    "📋 Motivo del préstamo:",
                    placeholder="Describe para qué necesitas el préstamo...",
                    height=100
                )
                
                fecha_solicitud = st.date_input(
                    "📅 Fecha de solicitud:",
                    value=datetime.now()
                )
            
            # Calcular y mostrar detalles del préstamo
            if monto_prestamo > 0:
                st.markdown("---")
                st.subheader("🧮 Detalles del Préstamo")
                
                detalles = calcular_detalles_prestamo(monto_prestamo, plazo_meses, configuracion['tasa_interes_mensual'])
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💵 Monto Principal", f"${monto_prestamo:,.2f}")
                
                with col2:
                    st.metric("💰 Interés Total", f"${detalles['interes_total']:,.2f}")
                
                with col3:
                    st.metric("🧮 Total a Pagar", f"${detalles['total_pagar']:,.2f}")
                
                with col4:
                    st.metric("📅 Pago Mensual", f"${detalles['pago_mensual']:,.2f}")
                
                st.info(f"""
                **📊 Desglose:**
                - **Interés mensual:** ${detalles['interes_mensual']:,.2f}
                - **Total a pagar:** ${detalles['total_pagar']:,.2f}
                - **Pago mensual:** ${detalles['pago_mensual']:,.2f} x {plazo_meses} meses
                - **Fecha de vencimiento:** {detalles['fecha_vencimiento']}
                """)
            
            # Botón de envío
            if st.form_submit_button("✅ Solicitar Préstamo", use_container_width=True):
                if monto_prestamo > 0 and proposito:
                    solicitar_prestamo(miembro_seleccionado, monto_prestamo, plazo_meses, proposito, fecha_solicitud, detalles)
                else:
                    st.error("❌ Completa todos los campos obligatorios")

def buscar_miembro_prestamo(configuracion):
    """Busca y valida un miembro para préstamo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener miembros con su ahorro y préstamos activos
            cursor.execute("""
                SELECT 
                    m.id_miembro,
                    m.nombre,
                    m.telefono,
                    COALESCE(SUM(a.monto), 0) as ahorro_actual,
                    COUNT(p.id_prestamo) as prestamos_activos
                FROM miembrogapc m
                LEFT JOIN aporte a ON m.id_miembro = a.id_miembro
                LEFT JOIN prestamo p ON m.id_miembro = p.id_miembro AND p.estado = 'aprobado'
                WHERE m.id_grupo = %s
                GROUP BY m.id_miembro, m.nombre, m.telefono
                ORDER BY m.nombre
            """, (id_grupo,))
            
            miembros = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if miembros:
                # Filtrar miembros que no pueden solicitar préstamo
                miembros_validos = []
                for miembro in miembros:
                    puede_solicitar = True
                    motivo = ""
                    
                    # Verificar si ya tiene préstamos activos (si no se permiten múltiples)
                    if not configuracion['permitir_multiples_prestamos'] and miembro['prestamos_activos'] > 0:
                        puede_solicitar = False
                        motivo = "❌ Ya tiene un préstamo activo"
                    
                    # Verificar si tiene ahorro suficiente
                    if miembro['ahorro_actual'] <= 0:
                        puede_solicitar = False
                        motivo = "❌ No tiene ahorro suficiente"
                    
                    if puede_solicitar:
                        miembros_validos.append(miembro)
                    else:
                        # Agregar con motivo para mostrar en la lista
                        miembro['motivo_rechazo'] = motivo
                        miembros_validos.append(miembro)
                
                # Crear lista de opciones
                opciones = []
                for miembro in miembros_validos:
                    if 'motivo_rechazo' in miembro:
                        opciones.append(f"❌ {miembro['id_miembro']} - {miembro['nombre']} ({miembro['motivo_rechazo']})")
                    else:
                        opciones.append(f"✅ {miembro['id_miembro']} - {miembro['nombre']} (Ahorro: ${miembro['ahorro_actual']:,.2f})")
                
                miembro_seleccionado = st.selectbox(
                    "👤 Selecciona el miembro solicitante:",
                    opciones,
                    key="selector_miembro_prestamo"
                )
                
                if miembro_seleccionado and miembro_seleccionado.startswith("✅"):
                    # Extraer ID del miembro seleccionado
                    miembro_id = int(miembro_seleccionado.split(" - ")[0].replace("✅ ", ""))
                    miembro_info = next(m for m in miembros_validos if m['id_miembro'] == miembro_id and 'motivo_rechazo' not in m)
                    return miembro_info
                elif miembro_seleccionado and miembro_seleccionado.startswith("❌"):
                    st.error("Este miembro no puede solicitar préstamos en este momento")
                    return None
                    
            else:
                st.info("📝 No hay miembros en este grupo.")
                return None
                
    except Exception as e:
        st.error(f"❌ Error al cargar miembros: {e}")
    
    return None

def calcular_detalles_prestamo(monto, plazo_meses, tasa_interes):
    """Calcula los detalles del préstamo"""
    # Calcular interés mensual (por cada $10)
    interes_mensual = (monto / 10) * tasa_interes
    
    # Calcular totales
    interes_total = interes_mensual * plazo_meses
    total_pagar = monto + interes_total
    pago_mensual = total_pagar / plazo_meses
    
    # Calcular fecha de vencimiento
    fecha_vencimiento = datetime.now() + relativedelta(months=plazo_meses)
    
    return {
        'interes_mensual': interes_mensual,
        'interes_total': interes_total,
        'total_pagar': total_pagar,
        'pago_mensual': pago_mensual,
        'fecha_vencimiento': fecha_vencimiento.strftime("%d/%m/%Y")
    }

def solicitar_prestamo(miembro, monto, plazo_meses, proposito, fecha_solicitud, detalles):
    """Guarda la solicitud de préstamo en la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Insertar préstamo
            cursor.execute("""
                INSERT INTO prestamo (
                    id_miembro, monto_prestado, proposito, 
                    fecha_vencimiento, plazo_meses, estado
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                miembro['id_miembro'],
                monto,
                proposito,
                datetime.now() + relativedelta(months=plazo_meses),
                plazo_meses,
                'aprobado'  # Podrías cambiar a 'pendiente' si necesitas aprobación
            ))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("🎉 ¡Préstamo solicitado exitosamente!")
            st.balloons()
            
    except Exception as e:
        st.error(f"❌ Error al solicitar préstamo: {e}")

def mostrar_historial_prestamos():
    """Muestra el historial completo de préstamos"""
    st.subheader("📋 Historial de Préstamos")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener todos los préstamos del grupo
            cursor.execute("""
                SELECT 
                    p.id_prestamo,
                    m.nombre as miembro,
                    p.monto_prestado,
                    p.proposito,
                    p.fecha_vencimiento,
                    p.plazo_meses,
                    p.estado,
                    COALESCE(SUM(pg.monto_capital), 0) as total_pagado,
                    (p.monto_prestado - COALESCE(SUM(pg.monto_capital), 0)) as saldo_pendiente
                FROM prestamo p
                JOIN miembrogapc m ON p.id_miembro = m.id_miembro
                LEFT JOIN pago pg ON p.id_prestamo = pg.id_prestamo
                WHERE m.id_grupo = %s
                GROUP BY p.id_prestamo, m.nombre, p.monto_prestado, p.proposito, 
                         p.fecha_vencimiento, p.plazo_meses, p.estado
                ORDER BY p.estado, p.fecha_vencimiento DESC
            """, (id_grupo,))
            
            prestamos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if prestamos:
                # Filtrar por estado
                estados = ["Todos"] + list(set(p['estado'] for p in prestamos))
                estado_seleccionado = st.selectbox("🔍 Filtrar por estado:", estados)
                
                if estado_seleccionado != "Todos":
                    prestamos = [p for p in prestamos if p['estado'] == estado_seleccionado]
                
                for prestamo in prestamos:
                    color_estado = "🟢" if prestamo['estado'] == 'aprobado' else "🔴" if prestamo['estado'] == 'rechazado' else "🟡"
                    
                    with st.expander(f"{color_estado} Préstamo #{prestamo['id_prestamo']} - {prestamo['miembro']} - ${prestamo['monto_prestado']:,.2f} ({prestamo['estado']})", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {prestamo['miembro']}")
                            st.write(f"**💵 Monto:** ${prestamo['monto_prestado']:,.2f}")
                            st.write(f"**📅 Vence:** {prestamo['fecha_vencimiento']}")
                            st.write(f"**📋 Propósito:** {prestamo['proposito']}")
                        with col2:
                            st.write(f"**📊 Estado:** {prestamo['estado']}")
                            st.write(f"**💰 Pagado:** ${prestamo['total_pagado']:,.2f}")
                            st.write(f"**📉 Pendiente:** ${prestamo['saldo_pendiente']:,.2f}")
                            st.write(f"**⏱️ Plazo:** {prestamo['plazo_meses']} meses")
            else:
                st.info("📝 No hay préstamos registrados en este grupo.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar historial: {e}")

def mostrar_prestamos_activos():
    """Muestra solo los préstamos activos"""
    st.subheader("📊 Préstamos Activos")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener préstamos activos
            cursor.execute("""
                SELECT 
                    p.id_prestamo,
                    m.nombre as miembro,
                    p.monto_prestado,
                    p.proposito,
                    p.fecha_vencimiento,
                    p.plazo_meses,
                    COALESCE(SUM(pg.monto_capital), 0) as total_pagado,
                    (p.monto_prestado - COALESCE(SUM(pg.monto_capital), 0)) as saldo_pendiente,
                    DATEDIFF(p.fecha_vencimiento, CURDATE()) as dias_restantes
                FROM prestamo p
                JOIN miembrogapc m ON p.id_miembro = m.id_miembro
                LEFT JOIN pago pg ON p.id_prestamo = pg.id_prestamo
                WHERE m.id_grupo = %s AND p.estado = 'aprobado'
                GROUP BY p.id_prestamo, m.nombre, p.monto_prestado, p.proposito, 
                         p.fecha_vencimiento, p.plazo_meses
                HAVING saldo_pendiente > 0
                ORDER BY p.fecha_vencimiento ASC
            """, (id_grupo,))
            
            prestamos_activos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if prestamos_activos:
                # Estadísticas
                total_activos = len(prestamos_activos)
                total_pendiente = sum(p['saldo_pendiente'] for p in prestamos_activos)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Préstamos Activos", total_activos)
                with col2:
                    st.metric("💰 Total Pendiente", f"${total_pendiente:,.2f}")
                with col3:
                    vencidos = len([p for p in prestamos_activos if p['dias_restantes'] < 0])
                    st.metric("⚠️ Préstamos Vencidos", vencidos)
                
                st.markdown("---")
                
                for prestamo in prestamos_activos:
                    # Determinar color según días restantes
                    if prestamo['dias_restantes'] < 0:
                        color = "🔴"  # Vencido
                        estado = f"VENCIDO (-{abs(prestamo['dias_restantes'])} días)"
                    elif prestamo['dias_restantes'] <= 30:
                        color = "🟡"  # Por vencer
                        estado = f"Por vencer ({prestamo['dias_restantes']} días)"
                    else:
                        color = "🟢"  # En tiempo
                        estado = f"En tiempo ({prestamo['dias_restantes']} días)"
                    
                    with st.expander(f"{color} {prestamo['miembro']} - ${prestamo['monto_prestado']:,.2f} - {estado}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**💵 Monto Original:** ${prestamo['monto_prestado']:,.2f}")
                            st.write(f"**💰 Total Pagado:** ${prestamo['total_pagado']:,.2f}")
                            st.write(f"**📋 Propósito:** {prestamo['proposito']}")
                        with col2:
                            st.write(f"**📉 Saldo Pendiente:** ${prestamo['saldo_pendiente']:,.2f}")
                            st.write(f"**📅 Fecha Vencimiento:** {prestamo['fecha_vencimiento']}")
                            st.write(f"**⏱️ Días Restantes:** {prestamo['dias_restantes']} días")
            else:
                st.success("✅ No hay préstamos activos en este momento.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar préstamos activos: {e}")
