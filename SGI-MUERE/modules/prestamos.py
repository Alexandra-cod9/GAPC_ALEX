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
        ["📋 Préstamos Activos", "✅ Préstamos Pagados", "📊 Historial Completo"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "📋 Préstamos Activos":
        mostrar_prestamos_activos()
    elif opcion == "✅ Préstamos Pagados":
        mostrar_prestamos_pagados()
    elif opcion == "📊 Historial Completo":
        mostrar_historial_completo()

def mostrar_prestamos_activos():
    """Muestra los préstamos activos con seguimiento de pagos"""
    st.subheader("📋 Préstamos Activos")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener préstamos activos con información de pagos
            cursor.execute("""
                SELECT 
                    p.id_prestamo,
                    m.nombre as miembro,
                    p.monto_prestado,
                    p.proposito,
                    p.fecha_vencimiento,
                    p.plazo_meses,
                    r.fecha as fecha_aprobacion,
                    COALESCE(SUM(pg.monto_capital), 0) as total_pagado,
                    (p.monto_prestado - COALESCE(SUM(pg.monto_capital), 0)) as saldo_pendiente,
                    DATEDIFF(p.fecha_vencimiento, CURDATE()) as dias_vencimiento
                FROM prestamo p
                JOIN miembrogapc m ON p.id_miembro = m.id_miembro
                JOIN reunion r ON p.id_reunion = r.id_reunion
                LEFT JOIN pago pg ON p.id_prestamo = pg.id_prestamo
                WHERE m.id_grupo = %s AND p.estado = 'aprobado'
                GROUP BY p.id_prestamo, m.nombre, p.monto_prestado, p.proposito, 
                         p.fecha_vencimiento, p.plazo_meses, r.fecha
                HAVING saldo_pendiente > 0
                ORDER BY p.fecha_vencimiento ASC
            """, (id_grupo,))
            
            prestamos_activos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if prestamos_activos:
                # Estadísticas
                total_prestamos = len(prestamos_activos)
                total_prestado = sum(p['monto_prestado'] for p in prestamos_activos)
                total_pendiente = sum(p['saldo_pendiente'] for p in prestamos_activos)
                total_pagado = sum(p['total_pagado'] for p in prestamos_activos)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Préstamos Activos", total_prestamos)
                with col2:
                    st.metric("💰 Total Prestado", f"${total_prestado:,.2f}")
                with col3:
                    st.metric("💵 Total Pagado", f"${total_pagado:,.2f}")
                with col4:
                    st.metric("📉 Total Pendiente", f"${total_pendiente:,.2f}")
                
                st.markdown("---")
                
                for prestamo in prestamos_activos:
                    # Calcular porcentaje pagado
                    porcentaje_pagado = (prestamo['total_pagado'] / prestamo['monto_prestado']) * 100 if prestamo['monto_prestado'] > 0 else 0
                    
                    # Determinar estado según días de vencimiento
                    if prestamo['dias_vencimiento'] < 0:
                        estado_icono = "🔴"
                        estado_texto = f"VENCIDO ({abs(prestamo['dias_vencimiento'])} días)"
                    elif prestamo['dias_vencimiento'] <= 7:
                        estado_icono = "🟡"
                        estado_texto = f"Por vencer ({prestamo['dias_vencimiento']} días)"
                    else:
                        estado_icono = "🟢"
                        estado_texto = f"Al día ({prestamo['dias_vencimiento']} días)"
                    
                    with st.expander(f"{estado_icono} {prestamo['miembro']} - ${prestamo['monto_prestado']:,.2f} - {estado_texto}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**👤 Miembro:** {prestamo['miembro']}")
                            st.write(f"**📋 Propósito:** {prestamo['proposito']}")
                            st.write(f"**💰 Monto Prestado:** ${prestamo['monto_prestado']:,.2f}")
                            st.write(f"**📅 Fecha Aprobación:** {prestamo['fecha_aprobacion']}")
                        
                        with col2:
                            st.write(f"**💵 Total Pagado:** ${prestamo['total_pagado']:,.2f}")
                            st.write(f"**📉 Saldo Pendiente:** ${prestamo['saldo_pendiente']:,.2f}")
                            st.write(f"**📆 Vencimiento:** {prestamo['fecha_vencimiento']}")
                            st.write(f"**⏰ Plazo:** {prestamo['plazo_meses']} meses")
                            
                            # Barra de progreso
                            st.write(f"**📊 Progreso de Pago:** {porcentaje_pagado:.1f}%")
                            st.progress(min(porcentaje_pagado / 100, 1.0))
                        
                        # Mostrar historial de pagos
                        mostrar_historial_pagos_prestamo(prestamo['id_prestamo'])
                        
                        # Botones de acción
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("💳 Registrar Pago Manual", key=f"pago_{prestamo['id_prestamo']}"):
                                st.session_state[f'mostrar_form_pago_{prestamo["id_prestamo"]}'] = True
                        
                        with col_btn2:
                            if st.button("✅ Marcar como Pagado", key=f"marcar_pagado_{prestamo['id_prestamo']}"):
                                marcar_prestamo_como_pagado(prestamo['id_prestamo'])
                                st.rerun()
                        
                        # Formulario de pago manual
                        if st.session_state.get(f'mostrar_form_pago_{prestamo["id_prestamo"]}', False):
                            with st.form(f"form_pago_{prestamo['id_prestamo']}"):
                                st.write("**💳 Registrar Pago Manual**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    monto_pago = st.number_input(
                                        "💵 Monto del pago:",
                                        min_value=0.0,
                                        max_value=float(prestamo['saldo_pendiente']),
                                        value=min(float(prestamo['saldo_pendiente']), 50.0),
                                        step=10.0
                                    )
                                with col2:
                                    fecha_pago = st.date_input(
                                        "📅 Fecha del pago:",
                                        value=datetime.now()
                                    )
                                
                                col_submit, col_cancel = st.columns(2)
                                with col_submit:
                                    if st.form_submit_button("✅ Guardar Pago", use_container_width=True):
                                        if monto_pago > 0:
                                            registrar_pago_manual(prestamo['id_prestamo'], monto_pago, fecha_pago)
                                            st.session_state[f'mostrar_form_pago_{prestamo["id_prestamo"]}'] = False
                                            st.rerun()
                                with col_cancel:
                                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                        st.session_state[f'mostrar_form_pago_{prestamo["id_prestamo"]}'] = False
                                        st.rerun()
            else:
                st.success("✅ No hay préstamos activos en este momento.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar préstamos activos: {e}")

def mostrar_historial_pagos_prestamo(id_prestamo):
    """Muestra el historial de pagos de un préstamo específico"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener pagos del préstamo
            cursor.execute("""
                SELECT 
                    pg.monto_capital,
                    pg.fecha_pago,
                    r.fecha as fecha_reunion
                FROM pago pg
                LEFT JOIN reunion r ON pg.id_reunion = r.id_reunion
                WHERE pg.id_prestamo = %s
                ORDER BY pg.fecha_pago DESC
            """, (id_prestamo,))
            
            pagos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if pagos:
                st.markdown("**💳 Historial de Pagos:**")
                for pago in pagos:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"📅 {pago['fecha_pago']}")
                    with col2:
                        st.write(f"💵 ${pago['monto_capital']:,.2f}")
                    with col3:
                        if pago['fecha_reunion']:
                            st.write(f"🎯 Reunión: {pago['fecha_reunion']}")
            else:
                st.info("📝 No hay pagos registrados para este préstamo.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar historial de pagos: {e}")

def registrar_pago_manual(id_prestamo, monto, fecha_pago):
    """Registra un pago manual para un préstamo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Insertar pago (sin id_reunion ya que es manual)
            cursor.execute("""
                INSERT INTO pago (id_prestamo, fecha_pago, monto_capital)
                VALUES (%s, %s, %s)
            """, (id_prestamo, fecha_pago, monto))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success(f"✅ Pago de ${monto:,.2f} registrado exitosamente!")
            
    except Exception as e:
        st.error(f"❌ Error al registrar pago: {e}")

def marcar_prestamo_como_pagado(id_prestamo):
    """Marca un préstamo como pagado completamente"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Cambiar estado a 'rechazado' (usamos este como 'pagado/completado')
            # Nota: Podrías necesitar agregar un estado 'pagado' en la tabla
            cursor.execute("""
                UPDATE prestamo 
                SET estado = 'rechazado'
                WHERE id_prestamo = %s
            """, (id_prestamo,))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("✅ Préstamo marcado como pagado completamente!")
            
    except Exception as e:
        st.error(f"❌ Error al marcar préstamo como pagado: {e}")

def mostrar_prestamos_pagados():
    """Muestra los préstamos que han sido pagados completamente"""
    st.subheader("✅ Préstamos Pagados")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener préstamos donde el saldo pendiente es 0 o estado es rechazado
            cursor.execute("""
                SELECT 
                    p.id_prestamo,
                    m.nombre as miembro,
                    p.monto_prestado,
                    p.proposito,
                    p.fecha_vencimiento,
                    r.fecha as fecha_aprobacion,
                    COALESCE(SUM(pg.monto_capital), 0) as total_pagado,
                    MAX(pg.fecha_pago) as fecha_ultimo_pago
                FROM prestamo p
                JOIN miembrogapc m ON p.id_miembro = m.id_miembro
                JOIN reunion r ON p.id_reunion = r.id_reunion
                LEFT JOIN pago pg ON p.id_prestamo = pg.id_prestamo
                WHERE m.id_grupo = %s 
                AND (p.estado = 'rechazado' OR p.monto_prestado <= COALESCE(SUM(pg.monto_capital), 0))
                GROUP BY p.id_prestamo, m.nombre, p.monto_prestado, p.proposito, 
                         p.fecha_vencimiento, r.fecha
                ORDER BY fecha_ultimo_pago DESC
            """, (id_grupo,))
            
            prestamos_pagados = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if prestamos_pagados:
                st.info(f"📊 Se encontraron {len(prestamos_pagados)} préstamos pagados")
                
                # Estadísticas
                total_monto = sum(p['monto_prestado'] for p in prestamos_pagados)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 Total Prestado (Pagados)", f"${total_monto:,.2f}")
                with col2:
                    st.metric("📊 Cantidad", len(prestamos_pagados))
                
                st.markdown("---")
                
                for prestamo in prestamos_pagados:
                    with st.expander(f"✅ {prestamo['miembro']} - ${prestamo['monto_prestado']:,.2f} - {prestamo['proposito'][:50]}...", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {prestamo['miembro']}")
                            st.write(f"**📋 Propósito:** {prestamo['proposito']}")
                            st.write(f"**💰 Monto Prestado:** ${prestamo['monto_prestado']:,.2f}")
                        with col2:
                            st.write(f"**💵 Total Pagado:** ${prestamo['total_pagado']:,.2f}")
                            st.write(f"**📅 Fecha Aprobación:** {prestamo['fecha_aprobacion']}")
                            if prestamo['fecha_ultimo_pago']:
                                st.write(f"**📆 Último Pago:** {prestamo['fecha_ultimo_pago']}")
                        
                        # Mostrar historial de pagos
                        mostrar_historial_pagos_prestamo(prestamo['id_prestamo'])
            else:
                st.info("📝 No hay préstamos pagados registrados.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar préstamos pagados: {e}")

def mostrar_historial_completo():
    """Muestra el historial completo de todos los préstamos"""
    st.subheader("📊 Historial Completo de Préstamos")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener todos los préstamos
            cursor.execute("""
                SELECT 
                    p.id_prestamo,
                    m.nombre as miembro,
                    p.monto_prestado,
                    p.proposito,
                    p.estado,
                    p.fecha_vencimiento,
                    p.plazo_meses,
                    r.fecha as fecha_aprobacion,
                    COALESCE(SUM(pg.monto_capital), 0) as total_pagado,
                    (p.monto_prestado - COALESCE(SUM(pg.monto_capital), 0)) as saldo_pendiente
                FROM prestamo p
                JOIN miembrogapc m ON p.id_miembro = m.id_miembro
                JOIN reunion r ON p.id_reunion = r.id_reunion
                LEFT JOIN pago pg ON p.id_prestamo = pg.id_prestamo
                WHERE m.id_grupo = %s
                GROUP BY p.id_prestamo, m.nombre, p.monto_prestado, p.proposito, 
                         p.estado, p.fecha_vencimiento, p.plazo_meses, r.fecha
                ORDER BY r.fecha DESC
            """, (id_grupo,))
            
            todos_prestamos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if todos_prestamos:
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    estados = ["Todos", "aprobado", "rechazado"]
                    estado_filtro = st.selectbox("🔍 Filtrar por estado:", estados)
                
                with col2:
                    miembros = ["Todos"] + list(set(p['miembro'] for p in todos_prestamos))
                    miembro_filtro = st.selectbox("👤 Filtrar por miembro:", miembros)
                
                # Aplicar filtros
                prestamos_filtrados = todos_prestamos
                if estado_filtro != "Todos":
                    prestamos_filtrados = [p for p in prestamos_filtrados if p['estado'] == estado_filtro]
                if miembro_filtro != "Todos":
                    prestamos_filtrados = [p for p in prestamos_filtrados if p['miembro'] == miembro_filtro]
                
                # Estadísticas filtradas
                total_filtrado = len(prestamos_filtrados)
                monto_total = sum(p['monto_prestado'] for p in prestamos_filtrados)
                pendiente_total = sum(p['saldo_pendiente'] for p in prestamos_filtrados)
                
                st.info(f"📊 Mostrando {total_filtrado} préstamos - Total: ${monto_total:,.2f} - Pendiente: ${pendiente_total:,.2f}")
                
                for prestamo in prestamos_filtrados:
                    # Icono según estado
                    if prestamo['saldo_pendiente'] <= 0 or prestamo['estado'] == 'rechazado':
                        icono = "✅"
                        estado_texto = "Pagado"
                    elif prestamo['estado'] == 'aprobado':
                        icono = "💳"
                        estado_texto = "Activo"
                    else:
                        icono = "❌"
                        estado_texto = prestamo['estado']
                    
                    with st.expander(f"{icono} {prestamo['miembro']} - ${prestamo['monto_prestado']:,.2f} - {estado_texto}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {prestamo['miembro']}")
                            st.write(f"**📋 Propósito:** {prestamo['proposito']}")
                            st.write(f"**💰 Monto Prestado:** ${prestamo['monto_prestado']:,.2f}")
                            st.write(f"**📅 Fecha Aprobación:** {prestamo['fecha_aprobacion']}")
                        with col2:
                            st.write(f"**💵 Total Pagado:** ${prestamo['total_pagado']:,.2f}")
                            st.write(f"**📉 Saldo Pendiente:** ${prestamo['saldo_pendiente']:,.2f}")
                            st.write(f"**📆 Vencimiento:** {prestamo['fecha_vencimiento']}")
                            st.write(f"**⏰ Plazo:** {prestamo['plazo_meses']} meses")
                            st.write(f"**🔒 Estado:** {prestamo['estado']}")
                        
                        # Mostrar historial de pagos
                        mostrar_historial_pagos_prestamo(prestamo['id_prestamo'])
            else:
                st.info("📝 No hay préstamos registrados en el historial.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar historial completo: {e}")
