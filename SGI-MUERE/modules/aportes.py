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

def mostrar_modulo_aportes():
    """Módulo de gestión de aportes"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 💰 Módulo de Aportes")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Menú de búsqueda
    st.subheader("🔍 Buscar Miembro")
    
    # Buscar miembro
    miembro_seleccionado = buscar_miembro()
    
    if miembro_seleccionado:
        mostrar_informacion_aportes(miembro_seleccionado)

def buscar_miembro():
    """Busca y selecciona un miembro del grupo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener miembros del grupo
            cursor.execute("""
                SELECT m.id_miembro, m.nombre, m.telefono, m.dui,
                       COALESCE(SUM(a.monto), 0) as total_ahorro
                FROM miembrogapc m
                LEFT JOIN aporte a ON m.id_miembro = a.id_miembro
                WHERE m.id_grupo = %s
                GROUP BY m.id_miembro, m.nombre, m.telefono, m.dui
                ORDER BY m.nombre
            """, (id_grupo,))
            
            miembros = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if miembros:
                # Crear lista de opciones para el selectbox
                opciones_miembros = [f"{m['id_miembro']} - {m['nombre']} (Ahorro: ${m['total_ahorro']:,.2f})" for m in miembros]
                
                # Selector de miembro
                miembro_seleccionado = st.selectbox(
                    "👤 Selecciona un miembro:",
                    opciones_miembros,
                    key="selector_miembro_aportes"
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

def mostrar_informacion_aportes(miembro):
    """Muestra la información detallada de aportes de un miembro"""
    
    st.markdown("---")
    st.subheader(f"📊 Resumen de Aportes - {miembro['nombre']}")
    
    # Obtener datos detallados del miembro
    datos_aportes = obtener_datos_aportes(miembro['id_miembro'])
    datos_prestamos = obtener_prestamos_pendientes(miembro['id_miembro'])
    
    # Mostrar información básica del miembro
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**📞 Teléfono:** {miembro['telefono']}")
    with col2:
        st.info(f"**🆔 DUI:** {miembro['dui']}")
    with col3:
        st.info(f"**💰 Ahorro Total:** ${datos_aportes['total_general']:,.2f}")
    
    st.markdown("---")
    
    # Mostrar resumen por tipos de aporte
    st.subheader("📈 Desglose por Tipo de Aporte")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "💵 Ahorro", 
            f"${datos_aportes['total_ahorro']:,.2f}",
            f"{datos_aportes['porcentaje_ahorro']:.1f}%"
        )
    
    with col2:
        st.metric(
            "🎯 Rifa", 
            f"${datos_aportes['total_rifa']:,.2f}",
            f"{datos_aportes['porcentaje_rifa']:.1f}%"
        )
    
    with col3:
        st.metric(
            "📤 Pago Préstamo", 
            f"${datos_aportes['total_pago_prestamo']:,.2f}",
            f"{datos_aportes['porcentaje_pago_prestamo']:.1f}%"
        )
    
    with col4:
        st.metric(
            "⚠️ Pago Multa", 
            f"${datos_aportes['total_pago_multa']:,.2f}",
            f"{datos_aportes['porcentaje_pago_multa']:.1f}%"
        )
    
    with col5:
        st.metric(
            "🔧 Otros", 
            f"${datos_aportes['total_otros']:,.2f}",
            f"{datos_aportes['porcentaje_otros']:.1f}%"
        )
    
    st.markdown("---")
    
    # Mostrar préstamos pendientes
    st.subheader("📋 Préstamos Pendientes")
    
    if datos_prestamos:
        total_prestamos_pendientes = sum(p['monto_restante'] for p in datos_prestamos)
        
        st.warning(f"**💳 Total en Préstamos Pendientes: ${total_prestamos_pendientes:,.2f}**")
        
        for prestamo in datos_prestamos:
            with st.expander(f"📅 Préstamo {prestamo['id_prestamo']} - ${prestamo['monto_prestado']:,.2f} (Vence: {prestamo['fecha_vencimiento']})", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Propósito:** {prestamo['proposito']}")
                with col2:
                    st.write(f"**Plazo:** {prestamo['plazo_meses']} meses")
                with col3:
                    st.write(f"**Pagado:** ${prestamo['monto_pagado']:,.2f}")
                    st.write(f"**Restante:** ${prestamo['monto_restante']:,.2f}")
    else:
        st.success("✅ No tiene préstamos pendientes")
    
    st.markdown("---")
    
    # Mostrar saldo neto final
    st.subheader("🧮 Saldo Neto Final")
    
    saldo_neto = datos_aportes['total_general'] - sum(p['monto_restante'] for p in datos_prestamos) if datos_prestamos else datos_aportes['total_general']
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**💰 Ahorro Total:** ${datos_aportes['total_general']:,.2f}")
    with col2:
        if datos_prestamos:
            st.info(f"**📉 Préstamos Pendientes:** -${sum(p['monto_restante'] for p in datos_prestamos):,.2f}")
    
    st.markdown("---")
    
    # Mostrar resultado final
    if saldo_neto >= 0:
        st.success(f"## 🎉 Saldo Neto Disponible: ${saldo_neto:,.2f}")
    else:
        st.error(f"## ⚠️ Saldo Negativo: ${saldo_neto:,.2f}")
    
    st.markdown("---")
    
    # Mostrar historial detallado de aportes
    st.subheader("📜 Historial Detallado de Aportes")
    
    historial_aportes = obtener_historial_aportes(miembro['id_miembro'])
    
    if historial_aportes:
        # Agrupar por reunión
        reuniones = {}
        for aporte in historial_aportes:
            if aporte['id_reunion'] not in reuniones:
                reuniones[aporte['id_reunion']] = {
                    'fecha': aporte['fecha_reunion'],
                    'aportes': []
                }
            reuniones[aporte['id_reunion']]['aportes'].append(aporte)
        
        # Mostrar por reunión
        for reunion_id, datos_reunion in reuniones.items():
            with st.expander(f"📅 Reunión del {datos_reunion['fecha']}", expanded=False):
                total_reunion = sum(a['monto'] for a in datos_reunion['aportes'])
                st.write(f"**Total en esta reunión: ${total_reunion:,.2f}**")
                
                for aporte in datos_reunion['aportes']:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Tipo:** {aporte['tipo']}")
                    with col2:
                        st.write(f"**Monto:** ${aporte['monto']:,.2f}")
                    with col3:
                        if aporte['observaciones']:
                            st.write(f"**Obs:** {aporte['observaciones']}")
    else:
        st.info("📝 No hay historial de aportes registrado")

def obtener_datos_aportes(id_miembro):
    """Obtiene los datos de aportes agrupados por tipo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener totales por tipo de aporte
            cursor.execute("""
                SELECT 
                    tipo,
                    COALESCE(SUM(monto), 0) as total
                FROM aporte 
                WHERE id_miembro = %s
                GROUP BY tipo
            """, (id_miembro,))
            
            resultados = cursor.fetchall()
            
            # Inicializar totales
            totales = {
                'Ahorro': 0,
                'Rifa': 0,
                'PagoPrestamo': 0,
                'PagoMulta': 0,
                'Otros': 0
            }
            
            # Llenar totales con datos reales
            for resultado in resultados:
                tipo = resultado['tipo']
                if tipo in totales:
                    totales[tipo] = float(resultado['total'])
            
            # Calcular total general
            total_general = sum(totales.values())
            
            # Calcular porcentajes
            porcentajes = {}
            for tipo, total in totales.items():
                if total_general > 0:
                    porcentajes[f'porcentaje_{tipo.lower()}'] = (total / total_general) * 100
                else:
                    porcentajes[f'porcentaje_{tipo.lower()}'] = 0
            
            cursor.close()
            conexion.close()
            
            return {
                'total_ahorro': totales['Ahorro'],
                'total_rifa': totales['Rifa'],
                'total_pago_prestamo': totales['PagoPrestamo'],
                'total_pago_multa': totales['PagoMulta'],
                'total_otros': totales['Otros'],
                'total_general': total_general,
                'porcentaje_ahorro': porcentajes['porcentaje_ahorro'],
                'porcentaje_rifa': porcentajes['porcentaje_rifa'],
                'porcentaje_pago_prestamo': porcentajes['porcentaje_pagoprestamo'],
                'porcentaje_pago_multa': porcentajes['porcentaje_pagomulta'],
                'porcentaje_otros': porcentajes['porcentaje_otros']
            }
            
    except Exception as e:
        st.error(f"❌ Error al obtener datos de aportes: {e}")
    
    return {
        'total_ahorro': 0,
        'total_rifa': 0,
        'total_pago_prestamo': 0,
        'total_pago_multa': 0,
        'total_otros': 0,
        'total_general': 0,
        'porcentaje_ahorro': 0,
        'porcentaje_rifa': 0,
        'porcentaje_pago_prestamo': 0,
        'porcentaje_pago_multa': 0,
        'porcentaje_otros': 0
    }

def obtener_prestamos_pendientes(id_miembro):
    """Obtiene los préstamos pendientes de pago"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener préstamos aprobados con pagos realizados
            cursor.execute("""
                SELECT 
                    p.id_prestamo,
                    p.monto_prestado,
                    p.proposito,
                    p.fecha_vencimiento,
                    p.plazo_meses,
                    p.estado,
                    COALESCE(SUM(pg.monto_capital), 0) as monto_pagado,
                    (p.monto_prestado - COALESCE(SUM(pg.monto_capital), 0)) as monto_restante
                FROM prestamo p
                LEFT JOIN pago pg ON p.id_prestamo = pg.id_prestamo
                WHERE p.id_miembro = %s AND p.estado = 'aprobado'
                GROUP BY p.id_prestamo, p.monto_prestado, p.proposito, p.fecha_vencimiento, p.plazo_meses, p.estado
                HAVING monto_restante > 0
            """, (id_miembro,))
            
            prestamos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            return prestamos
            
    except Exception as e:
        st.error(f"❌ Error al obtener préstamos pendientes: {e}")
    
    return []

def obtener_historial_aportes(id_miembro):
    """Obtiene el historial completo de aportes"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            cursor.execute("""
                SELECT 
                    a.id_aporte,
                    a.monto,
                    a.tipo,
                    a.id_reunion,
                    r.fecha as fecha_reunion,
                    a.observaciones
                FROM aporte a
                JOIN reunion r ON a.id_reunion = r.id_reunion
                WHERE a.id_miembro = %s
                ORDER BY r.fecha DESC, a.id_aporte DESC
            """, (id_miembro,))
            
            historial = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            return historial
            
    except Exception as e:
        st.error(f"❌ Error al obtener historial de aportes: {e}")
    
    return []
