import streamlit as st
import pymysql
from datetime import datetime

def mostrar_modulo_multas():
    """Módulo de gestión de multas"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# ⚖️ Módulo de Gestión de Multas")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Menú de opciones
    opcion = st.radio(
        "Selecciona una acción:",
        ["➕ Nueva Multa", "📋 Multas Activas", "📊 Historial de Multas", "💳 Pagos de Multas"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "➕ Nueva Multa":
        mostrar_nueva_multa()
    elif opcion == "📋 Multas Activas":
        mostrar_multas_activas()
    elif opcion == "📊 Historial de Multas":
        mostrar_historial_multas()
    elif opcion == "💳 Pagos de Multas":
        mostrar_pagos_multas()

def mostrar_nueva_multa():
    """Interfaz para registrar una nueva multa"""
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
                monto_multa = st.number_input(
                    "💰 Monto de la multa:",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    help="Monto de la multa a aplicar"
                )
                
                fecha_multa = st.date_input(
                    "📅 Fecha de la multa:",
                    value=datetime.now()
                )
            
            with col2:
                motivo = st.text_area(
                    "📋 Motivo de la multa:",
                    placeholder="Describe el motivo de la multa...",
                    height=100,
                    help="Explica claramente por qué se aplica esta multa"
                )
                
                tipo_multa = st.selectbox(
                    "🔖 Tipo de multa:",
                    ["Retraso en aporte", "Falta a reunión", "Incumplimiento de reglas", "Otro"]
                )
            
            # Botón de envío
            submitted = st.form_submit_button("⚖️ Aplicar Multa", use_container_width=True)
            
            if submitted:
                if monto_multa > 0 and motivo.strip():
                    aplicar_multa(miembro_seleccionado, monto_multa, motivo, tipo_multa, fecha_multa)
                    st.success("✅ Multa aplicada exitosamente!")
                    st.rerun()
                else:
                    st.error("❌ Completa todos los campos obligatorios: monto y motivo")

def buscar_miembro_multa():
    """Busca y selecciona un miembro para aplicar multa"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener miembros del grupo
            cursor.execute("""
                SELECT 
                    id_miembro,
                    nombre,
                    telefono
                FROM miembrogapc 
                WHERE id_grupo = %s
                ORDER BY nombre
            """, (id_grupo,))
            
            miembros = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if miembros:
                # Crear lista de opciones
                opciones = [f"{m['id_miembro']} - {m['nombre']} ({m['telefono']})" for m in miembros]
                
                miembro_seleccionado = st.selectbox(
                    "👤 Selecciona el miembro:",
                    opciones,
                    key="selector_miembro_multa"
                )
                
                if miembro_seleccionado:
                    # Extraer ID del miembro seleccionado
                    miembro_id = int(miembro_seleccionado.split(" - ")[0])
                    miembro_info = next(m for m in miembros if m['id_miembro'] == miembro_id)
                    return miembro_info
                    
            else:
                st.info("📝 No hay miembros en este grupo.")
                return None
                
    except Exception as e:
        st.error(f"❌ Error al cargar miembros: {e}")
    
    return None

def aplicar_multa(miembro, monto, motivo, tipo_multa, fecha_multa):
    """Guarda la multa en la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Insertar multa
            cursor.execute("""
                INSERT INTO multa (
                    id_miembro, monto, motivo, tipo_multa, fecha_multa, estado
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                miembro['id_miembro'],
                monto,
                motivo,
                tipo_multa,
                fecha_multa,
                'pendiente'  # Estado inicial: pendiente de pago
            ))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("🎉 Multa registrada exitosamente!")
            st.balloons()
            
    except Exception as e:
        st.error(f"❌ Error al aplicar multa: {e}")

def mostrar_multas_activas():
    """Muestra las multas pendientes de pago"""
    st.subheader("📋 Multas Activas (Pendientes de Pago)")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener multas pendientes
            cursor.execute("""
                SELECT 
                    m.id_multa,
                    mb.nombre as miembro,
                    m.monto,
                    m.motivo,
                    m.tipo_multa,
                    m.fecha_multa,
                    m.estado,
                    COALESCE(SUM(CASE WHEN a.tipo_aporte = 'pago_multa' THEN a.monto ELSE 0 END), 0) as total_pagado,
                    (m.monto - COALESCE(SUM(CASE WHEN a.tipo_aporte = 'pago_multa' THEN a.monto ELSE 0 END), 0)) as saldo_pendiente
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                LEFT JOIN aporte a ON m.id_multa = a.id_multa
                WHERE mb.id_grupo = %s AND m.estado = 'pendiente'
                GROUP BY m.id_multa, mb.nombre, m.monto, m.motivo, m.tipo_multa, m.fecha_multa, m.estado
                HAVING saldo_pendiente > 0
                ORDER BY m.fecha_multa ASC
            """, (id_grupo,))
            
            multas_pendientes = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas_pendientes:
                # Estadísticas
                total_multas = len(multas_pendientes)
                total_pendiente = sum(m['saldo_pendiente'] for m in multas_pendientes)
                total_recaudado = sum(m['total_pagado'] for m in multas_pendientes)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Multas Activas", total_multas)
                with col2:
                    st.metric("💰 Total Pendiente", f"${total_pendiente:,.2f}")
                with col3:
                    st.metric("💳 Total Recaudado", f"${total_recaudado:,.2f}")
                
                st.markdown("---")
                
                for multa in multas_pendientes:
                    porcentaje_pagado = (multa['total_pagado'] / multa['monto']) * 100
                    
                    with st.expander(f"⚖️ {multa['miembro']} - ${multa['monto']:,.2f} - {multa['tipo_multa']} ({porcentaje_pagado:.1f}% pagado)", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**💰 Monto Multa:** ${multa['monto']:,.2f}")
                            st.write(f"**📅 Fecha Multa:** {multa['fecha_multa']}")
                            st.write(f"**🔖 Tipo:** {multa['tipo_multa']}")
                        with col2:
                            st.write(f"**💳 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📉 Saldo Pendiente:** ${multa['saldo_pendiente']:,.2f}")
                            st.write(f"**📊 Progreso:** {porcentaje_pagado:.1f}%")
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                        
                        # Barra de progreso visual
                        st.progress(porcentaje_pagado / 100)
                        
                        # Botón para registrar pago manual (opcional)
                        with st.form(f"form_pago_multa_{multa['id_multa']}"):
                            st.write("**💳 Registrar Pago Parcial:**")
                            col1, col2 = st.columns(2)
                            with col1:
                                monto_pago = st.number_input(
                                    "Monto a pagar:",
                                    min_value=0.0,
                                    max_value=float(multa['saldo_pendiente']),
                                    value=float(multa['saldo_pendiente']),
                                    step=10.0,
                                    key=f"monto_pago_{multa['id_multa']}"
                                )
                            with col2:
                                fecha_pago = st.date_input(
                                    "Fecha de pago:",
                                    value=datetime.now(),
                                    key=f"fecha_pago_{multa['id_multa']}"
                                )
                            
                            if st.form_submit_button("💳 Registrar Pago", use_container_width=True):
                                registrar_pago_multa(multa['id_multa'], monto_pago, fecha_pago, multa['id_miembro'])
                                st.success("✅ Pago registrado exitosamente!")
                                st.rerun()
            else:
                st.success("✅ No hay multas pendientes de pago.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas activas: {e}")

def mostrar_historial_multas():
    """Muestra el historial completo de multas"""
    st.subheader("📊 Historial Completo de Multas")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener todas las multas
            cursor.execute("""
                SELECT 
                    m.id_multa,
                    mb.nombre as miembro,
                    m.monto,
                    m.motivo,
                    m.tipo_multa,
                    m.fecha_multa,
                    m.estado,
                    COALESCE(SUM(CASE WHEN a.tipo_aporte = 'pago_multa' THEN a.monto ELSE 0 END), 0) as total_pagado,
                    (m.monto - COALESCE(SUM(CASE WHEN a.tipo_aporte = 'pago_multa' THEN a.monto ELSE 0 END), 0)) as saldo_pendiente
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                LEFT JOIN aporte a ON m.id_multa = a.id_multa
                WHERE mb.id_grupo = %s
                GROUP BY m.id_multa, mb.nombre, m.monto, m.motivo, m.tipo_multa, m.fecha_multa, m.estado
                ORDER BY m.fecha_multa DESC
            """, (id_grupo,))
            
            multas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas:
                # Filtrar por estado
                estados = ["Todos", "pendiente", "pagada", "cancelada"]
                estado_seleccionado = st.selectbox("🔍 Filtrar por estado:", estados)
                
                if estado_seleccionado != "Todos":
                    multas = [m for m in multas if m['estado'] == estado_seleccionado]
                
                # Estadísticas rápidas
                multas_pendientes = len([m for m in multas if m['estado'] == 'pendiente'])
                multas_pagadas = len([m for m in multas if m['estado'] == 'pagada'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Multas", len(multas))
                with col2:
                    st.metric("⏳ Pendientes", multas_pendientes)
                with col3:
                    st.metric("✅ Pagadas", multas_pagadas)
                
                st.markdown("---")
                
                for multa in multas:
                    color_estado = "🟢" if multa['estado'] == 'pagada' else "🟡" if multa['estado'] == 'pendiente' else "🔴"
                    estado_texto = "Pagada" if multa['estado'] == 'pagada' else "Pendiente" if multa['estado'] == 'pendiente' else "Cancelada"
                    
                    with st.expander(f"{color_estado} {multa['miembro']} - ${multa['monto']:,.2f} - {multa['tipo_multa']} ({estado_texto})", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**💰 Monto Original:** ${multa['monto']:,.2f}")
                            st.write(f"**📅 Fecha Multa:** {multa['fecha_multa']}")
                            st.write(f"**🔖 Tipo:** {multa['tipo_multa']}")
                        with col2:
                            st.write(f"**📊 Estado:** {estado_texto}")
                            st.write(f"**💳 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📉 Saldo Pendiente:** ${multa['saldo_pendiente']:,.2f}")
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
            else:
                st.info("📝 No hay multas registradas en este grupo.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar historial: {e}")

def mostrar_pagos_multas():
    """Muestra el historial de pagos de multas"""
    st.subheader("💳 Historial de Pagos de Multas")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener pagos de multas
            cursor.execute("""
                SELECT 
                    a.id_aporte,
                    a.fecha_aporte,
                    a.monto,
                    a.tipo_aporte,
                    mb.nombre as miembro,
                    m.motivo,
                    m.tipo_multa,
                    m.monto as monto_multa_original
                FROM aporte a
                JOIN multa m ON a.id_multa = m.id_multa
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                WHERE mb.id_grupo = %s AND a.tipo_aporte = 'pago_multa'
                ORDER BY a.fecha_aporte DESC
            """, (id_grupo,))
            
            pagos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if pagos:
                # Estadísticas
                total_pagos = len(pagos)
                total_recaudado = sum(p['monto'] for p in pagos)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📊 Total de Pagos", total_pagos)
                with col2:
                    st.metric("💰 Total Recaudado", f"${total_recaudado:,.2f}")
                
                st.markdown("---")
                
                for pago in pagos:
                    with st.expander(f"💳 {pago['miembro']} - ${pago['monto']:,.2f} - {pago['fecha_aporte']}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {pago['miembro']}")
                            st.write(f"**💰 Monto Pagado:** ${pago['monto']:,.2f}")
                            st.write(f"**📅 Fecha Pago:** {pago['fecha_aporte']}")
                        with col2:
                            st.write(f"**🔖 Tipo Multa:** {pago['tipo_multa']}")
                            st.write(f"**📋 Motivo Multa:** {pago['motivo']}")
                            st.write(f"**💰 Monto Multa Original:** ${pago['monto_multa_original']:,.2f}")
            else:
                st.info("📝 No hay pagos de multas registrados.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar pagos: {e}")

def registrar_pago_multa(id_multa, monto_pago, fecha_pago, id_miembro):
    """Registra un pago parcial o total de multa"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Registrar el pago como aporte de tipo 'pago_multa'
            cursor.execute("""
                INSERT INTO aporte (
                    id_miembro, monto, tipo_aporte, fecha_aporte, id_multa
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                id_miembro,
                monto_pago,
                'pago_multa',
                fecha_pago,
                id_multa
            ))
            
            # Verificar si la multa está completamente pagada
            cursor.execute("""
                SELECT 
                    m.monto,
                    COALESCE(SUM(a.monto), 0) as total_pagado
                FROM multa m
                LEFT JOIN aporte a ON m.id_multa = a.id_multa AND a.tipo_aporte = 'pago_multa'
                WHERE m.id_multa = %s
                GROUP BY m.monto
            """, (id_multa,))
            
            resultado = cursor.fetchone()
            
            # Actualizar estado de la multa si está completamente pagada
            if resultado and resultado['total_pagado'] >= resultado['monto']:
                cursor.execute("""
                    UPDATE multa 
                    SET estado = 'pagada' 
                    WHERE id_multa = %s
                """, (id_multa,))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
    except Exception as e:
        st.error(f"❌ Error al registrar pago: {e}")

# Función para integrar con el módulo de aportes
def procesar_pago_multa_en_aporte(id_miembro, monto, fecha_aporte, id_multa=None):
    """Función para ser llamada desde el módulo de aportes cuando se registra un pago de multa"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            if id_multa:
                # Pago específico para una multa
                registrar_pago_multa(id_multa, monto, fecha_aporte, id_miembro)
            else:
                # Aplicar pago a multas más antiguas primero (método FIFO)
                cursor.execute("""
                    SELECT id_multa, monto, 
                           (monto - COALESCE((
                               SELECT SUM(a.monto) 
                               FROM aporte a 
                               WHERE a.id_multa = m.id_multa 
                               AND a.tipo_aporte = 'pago_multa'
                           ), 0)) as saldo_pendiente
                    FROM multa m
                    WHERE m.id_miembro = %s AND m.estado = 'pendiente'
                    ORDER BY m.fecha_multa ASC
                """, (id_miembro,))
                
                multas_pendientes = cursor.fetchall()
                monto_restante = monto
                
                for multa in multas_pendientes:
                    if monto_restante <= 0:
                        break
                    
                    pago_a_aplicar = min(monto_restante, multa['saldo_pendiente'])
                    if pago_a_aplicar > 0:
                        registrar_pago_multa(multa['id_multa'], pago_a_aplicar, fecha_aporte, id_miembro)
                        monto_restante -= pago_a_aplicar
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
    except Exception as e:
        st.error(f"❌ Error al procesar pago de multa: {e}")

def obtener_multas_pendientes_miembro(id_miembro):
    """Obtiene las multas pendientes de un miembro específico"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            cursor.execute("""
                SELECT 
                    m.id_multa,
                    m.monto,
                    m.motivo,
                    m.tipo_multa,
                    m.fecha_multa,
                    (m.monto - COALESCE(SUM(CASE WHEN a.tipo_aporte = 'pago_multa' THEN a.monto ELSE 0 END), 0)) as saldo_pendiente
                FROM multa m
                LEFT JOIN aporte a ON m.id_multa = a.id_multa
                WHERE m.id_miembro = %s AND m.estado = 'pendiente'
                GROUP BY m.id_multa, m.monto, m.motivo, m.tipo_multa, m.fecha_multa
                HAVING saldo_pendiente > 0
                ORDER BY m.fecha_multa ASC
            """, (id_miembro,))
            
            multas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            return multas
            
    except Exception as e:
        st.error(f"❌ Error al obtener multas pendientes: {e}")
        return []
