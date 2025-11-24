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

def mostrar_modulo_multas():
    """Módulo de gestión de multas"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# ⚠️ Módulo de Multas")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Menú de opciones
    opcion = st.radio(
        "Selecciona una acción:",
        ["➕ Nueva Multa", "📋 Multas Activas", "✅ Multas Pagadas", "📊 Historial Completo"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "➕ Nueva Multa":
        mostrar_nueva_multa()
    elif opcion == "📋 Multas Activas":
        mostrar_multas_activas()
    elif opcion == "✅ Multas Pagadas":
        mostrar_multas_pagadas()
    elif opcion == "📊 Historial Completo":
        mostrar_historial_completo()

def mostrar_nueva_multa():
    """Interfaz para crear una nueva multa"""
    st.subheader("➕ Registrar Nueva Multa")
    
    with st.form("form_nueva_multa"):
        # Buscar miembro
        miembro_seleccionado = buscar_miembro_multa()
        
        if miembro_seleccionado:
            st.markdown("---")
            
            # Mostrar información del miembro
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**👤 Miembro:** {miembro_seleccionado['nombre']}")
            with col2:
                st.info(f"**📞 Teléfono:** {miembro_seleccionado['telefono']}")
            
            # Datos de la multa
            st.subheader("📝 Datos de la Multa")
            
            col1, col2 = st.columns(2)
            
            with col1:
                motivo = st.text_area(
                    "📋 Motivo de la multa:",
                    placeholder="Describe la razón de la multa...",
                    height=100,
                    help="Ej: Falta a reunión, Retraso en pago, Incumplimiento de acuerdo, etc."
                )
                
                fecha_multa = st.date_input(
                    "📅 Fecha de la multa:",
                    value=datetime.now()
                )
            
            with col2:
                monto_multa = st.number_input(
                    "💵 Monto de la multa:",
                    min_value=0.0,
                    value=5.00,
                    step=1.0,
                    help="Monto a multar al miembro"
                )
                
                # Selector de estado (podría ser automático como "activo")
                estado_multa = st.selectbox(
                    "🔒 Estado de la multa:",
                    ["activo", "pagado", "otro"],
                    help="Estado inicial de la multa"
                )
            
            # Botón de envío
            if st.form_submit_button("💾 Registrar Multa", use_container_width=True):
                if motivo and monto_multa > 0:
                    registrar_multa(miembro_seleccionado, motivo, monto_multa, fecha_multa, estado_multa)
                else:
                    st.error("❌ Completa todos los campos obligatorios")

def buscar_miembro_multa():
    """Busca y selecciona un miembro para asignar multa"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener miembros del grupo
            cursor.execute("""
                SELECT 
                    m.id_miembro,
                    m.nombre,
                    m.telefono,
                    COUNT(mt.id_multa) as multas_activas
                FROM miembrogapc m
                LEFT JOIN multa mt ON m.id_miembro = mt.id_miembro AND mt.id_estado = 1
                WHERE m.id_grupo = %s
                GROUP BY m.id_miembro, m.nombre, m.telefono
                ORDER BY m.nombre
            """, (id_grupo,))
            
            miembros = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if miembros:
                # Crear lista de opciones
                opciones = []
                for miembro in miembros:
                    if miembro['multas_activas'] > 0:
                        opciones.append(f"⚠️ {miembro['id_miembro']} - {miembro['nombre']} ({miembro['multas_activas']} multas activas)")
                    else:
                        opciones.append(f"✅ {miembro['id_miembro']} - {miembro['nombre']}")
                
                miembro_seleccionado = st.selectbox(
                    "👤 Selecciona el miembro a multar:",
                    opciones,
                    key="selector_miembro_multa"
                )
                
                if miembro_seleccionado:
                    # Extraer ID del miembro seleccionado
                    miembro_id = int(miembro_seleccionado.split(" - ")[0].replace("⚠️ ", "").replace("✅ ", ""))
                    miembro_info = next(m for m in miembros if m['id_miembro'] == miembro_id)
                    return miembro_info
                    
            else:
                st.info("📝 No hay miembros en este grupo.")
                return None
                
    except Exception as e:
        st.error(f"❌ Error al cargar miembros: {e}")
    
    return None

def registrar_multa(miembro, motivo, monto, fecha, estado):
    """Registra una nueva multa en la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Mapear estado a id_estado
            estado_map = {
                "activo": 1,  # activo
                "pagado": 3,  # pagado
                "otro": 4     # otro
            }
            id_estado = estado_map.get(estado, 1)
            
            # Insertar multa
            cursor.execute("""
                INSERT INTO multa (
                    id_miembro, motivo, monto, id_estado, fecha_creacion
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                miembro['id_miembro'],
                motivo,
                monto,
                id_estado,
                fecha
            ))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("🎉 ¡Multa registrada exitosamente!")
            st.balloons()
            
    except Exception as e:
        st.error(f"❌ Error al registrar multa: {e}")

def mostrar_multas_activas():
    """Muestra las multas activas con seguimiento de pagos"""
    st.subheader("📋 Multas Activas")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener multas activas con información de pagos
            cursor.execute("""
                SELECT 
                    mt.id_multa,
                    m.nombre as miembro,
                    mt.motivo,
                    mt.monto as monto_original,
                    mt.fecha_creacion,
                    e.nombre_estado,
                    COALESCE(SUM(
                        CASE WHEN a.tipo = 'PagoMulta' THEN a.monto ELSE 0 END
                    ), 0) as total_pagado,
                    (mt.monto - COALESCE(SUM(
                        CASE WHEN a.tipo = 'PagoMulta' THEN a.monto ELSE 0 END
                    ), 0)) as saldo_pendiente
                FROM multa mt
                JOIN miembrogapc m ON mt.id_miembro = m.id_miembro
                JOIN estado e ON mt.id_estado = e.id_estado
                LEFT JOIN aporte a ON mt.id_miembro = a.id_miembro AND a.tipo = 'PagoMulta'
                WHERE m.id_grupo = %s AND e.nombre_estado = 'activo'
                GROUP BY mt.id_multa, m.nombre, mt.motivo, mt.monto, mt.fecha_creacion, e.nombre_estado
                HAVING saldo_pendiente > 0
                ORDER BY mt.fecha_creacion DESC
            """, (id_grupo,))
            
            multas_activas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas_activas:
                # Estadísticas
                total_multas = len(multas_activas)
                total_pendiente = sum(m['saldo_pendiente'] for m in multas_activas)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Multas Activas", total_multas)
                with col2:
                    st.metric("💰 Total Pendiente", f"${total_pendiente:,.2f}")
                with col3:
                    promedio_multa = total_pendiente / total_multas if total_multas > 0 else 0
                    st.metric("📈 Promedio por Multa", f"${promedio_multa:,.2f}")
                
                st.markdown("---")
                
                for multa in multas_activas:
                    # Calcular porcentaje pagado
                    porcentaje_pagado = (multa['total_pagado'] / multa['monto_original']) * 100
                    
                    with st.expander(f"⚠️ {multa['miembro']} - ${multa['monto_original']:,.2f} - {multa['motivo'][:50]}...", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                            st.write(f"**📅 Fecha:** {multa['fecha_creacion']}")
                            st.write(f"**💰 Monto Original:** ${multa['monto_original']:,.2f}")
                        
                        with col2:
                            st.write(f"**💵 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📉 Saldo Pendiente:** ${multa['saldo_pendiente']:,.2f}")
                            st.write(f"**📊 Progreso:** {porcentaje_pagado:.1f}%")
                            
                            # Barra de progreso
                            st.progress(porcentaje_pagado / 100)
                        
                        # Mostrar historial de pagos de esta multa
                        mostrar_historial_pagos_multa(multa['id_multa'])
                        
                        # Botón para marcar como pagada manualmente
                        if st.button("✅ Marcar como Pagada", key=f"pagar_{multa['id_multa']}"):
                            marcar_multa_como_pagada(multa['id_multa'])
                            st.rerun()
            else:
                st.success("✅ No hay multas activas en este momento.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas activas: {e}")

def mostrar_historial_pagos_multa(id_multa):
    """Muestra el historial de pagos de una multa específica"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener pagos específicos de esta multa
            cursor.execute("""
                SELECT 
                    a.monto,
                    r.fecha as fecha_pago,
                    a.tipo,
                    a.observaciones
                FROM aporte a
                JOIN reunion r ON a.id_reunion = r.id_reunion
                JOIN multa mt ON a.id_miembro = mt.id_miembro
                WHERE mt.id_multa = %s AND a.tipo = 'PagoMulta'
                ORDER BY r.fecha DESC
            """, (id_multa,))
            
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
                        st.write(f"${pago['monto']:,.2f}")
                    with col3:
                        if pago['observaciones']:
                            st.write(f"📝 {pago['observaciones']}")
            else:
                st.info("📝 No hay pagos registrados para esta multa.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar historial de pagos: {e}")

def marcar_multa_como_pagada(id_multa):
    """Marca una multa como pagada manualmente"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Actualizar estado de la multa a "pagado" (id_estado = 3)
            cursor.execute("""
                UPDATE multa 
                SET id_estado = 3 
                WHERE id_multa = %s
            """, (id_multa,))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("✅ Multa marcada como pagada exitosamente!")
            
    except Exception as e:
        st.error(f"❌ Error al marcar multa como pagada: {e}")

def mostrar_multas_pagadas():
    """Muestra las multas que han sido pagadas completamente"""
    st.subheader("✅ Multas Pagadas")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener multas pagadas
            cursor.execute("""
                SELECT 
                    mt.id_multa,
                    m.nombre as miembro,
                    mt.motivo,
                    mt.monto,
                    mt.fecha_creacion,
                    MAX(r.fecha) as fecha_ultimo_pago,
                    COALESCE(SUM(
                        CASE WHEN a.tipo = 'PagoMulta' THEN a.monto ELSE 0 END
                    ), 0) as total_pagado
                FROM multa mt
                JOIN miembrogapc m ON mt.id_miembro = m.id_miembro
                JOIN estado e ON mt.id_estado = e.id_estado
                LEFT JOIN aporte a ON mt.id_miembro = a.id_miembro AND a.tipo = 'PagoMulta'
                WHERE m.id_grupo = %s AND e.nombre_estado = 'pagado'
                GROUP BY mt.id_multa, m.nombre, mt.motivo, mt.monto, mt.fecha_creacion
                ORDER BY fecha_ultimo_pago DESC
            """, (id_grupo,))
            
            multas_pagadas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas_pagadas:
                st.info(f"📊 Se encontraron {len(multas_pagadas)} multas pagadas")
                
                for multa in multas_pagadas:
                    with st.expander(f"✅ {multa['miembro']} - ${multa['monto']:,.2f} - {multa['motivo'][:50]}...", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                            st.write(f"**📅 Fecha Multa:** {multa['fecha_creacion']}")
                        with col2:
                            st.write(f"**💰 Monto:** ${multa['monto']:,.2f}")
                            st.write(f"**💵 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📅 Último Pago:** {multa['fecha_ultimo_pago']}")
            else:
                st.info("📝 No hay multas pagadas registradas.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas pagadas: {e}")

def mostrar_historial_completo():
    """Muestra el historial completo de todas las multas"""
    st.subheader("📊 Historial Completo de Multas")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener todas las multas
            cursor.execute("""
                SELECT 
                    mt.id_multa,
                    m.nombre as miembro,
                    mt.motivo,
                    mt.monto,
                    mt.fecha_creacion,
                    e.nombre_estado as estado,
                    COALESCE(SUM(
                        CASE WHEN a.tipo = 'PagoMulta' THEN a.monto ELSE 0 END
                    ), 0) as total_pagado,
                    (mt.monto - COALESCE(SUM(
                        CASE WHEN a.tipo = 'PagoMulta' THEN a.monto ELSE 0 END
                    ), 0)) as saldo_pendiente
                FROM multa mt
                JOIN miembrogapc m ON mt.id_miembro = m.id_miembro
                JOIN estado e ON mt.id_estado = e.id_estado
                LEFT JOIN aporte a ON mt.id_miembro = a.id_miembro AND a.tipo = 'PagoMulta'
                WHERE m.id_grupo = %s
                GROUP BY mt.id_multa, m.nombre, mt.motivo, mt.monto, mt.fecha_creacion, e.nombre_estado
                ORDER BY mt.fecha_creacion DESC
            """, (id_grupo,))
            
            todas_multas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if todas_multas:
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    estados = ["Todos"] + list(set(m['estado'] for m in todas_multas))
                    estado_filtro = st.selectbox("🔍 Filtrar por estado:", estados)
                
                with col2:
                    miembros = ["Todos"] + list(set(m['miembro'] for m in todas_multas))
                    miembro_filtro = st.selectbox("👤 Filtrar por miembro:", miembros)
                
                # Aplicar filtros
                multas_filtradas = todas_multas
                if estado_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['estado'] == estado_filtro]
                if miembro_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['miembro'] == miembro_filtro]
                
                # Estadísticas filtradas
                total_filtrado = len(multas_filtradas)
                monto_total = sum(m['monto'] for m in multas_filtradas)
                pendiente_total = sum(m['saldo_pendiente'] for m in multas_filtradas)
                
                st.info(f"📊 Mostrando {total_filtrado} multas - Total: ${monto_total:,.2f} - Pendiente: ${pendiente_total:,.2f}")
                
                for multa in multas_filtradas:
                    # Icono según estado
                    icono = "✅" if multa['estado'] == 'pagado' else "⚠️" if multa['estado'] == 'activo' else "🔶"
                    
                    with st.expander(f"{icono} {multa['miembro']} - ${multa['monto']:,.2f} - {multa['estado']}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                            st.write(f"**📅 Fecha:** {multa['fecha_creacion']}")
                        with col2:
                            st.write(f"**💰 Monto:** ${multa['monto']:,.2f}")
                            st.write(f"**💵 Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📉 Pendiente:** ${multa['saldo_pendiente']:,.2f}")
                            st.write(f"**🔒 Estado:** {multa['estado']}")
            else:
                st.info("📝 No hay multas registradas en el historial.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar historial completo: {e}")
