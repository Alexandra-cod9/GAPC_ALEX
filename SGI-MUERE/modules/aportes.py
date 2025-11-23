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
    
    # CORRECCIÓN: Verificar si hay préstamos pendientes de manera segura
    total_prestamos_pendientes = 0
    if datos_prestamos and len(datos_prestamos) > 0:
        # Calcular total de préstamos pendientes de manera segura
        total_prestamos_pendientes = sum(float(p.get('monto_restante', 0)) for p in datos_prestamos)
        
        st.warning(f"**💳 Total en Préstamos Pendientes: ${total_prestamos_pendientes:,.2f}**")
        
        for prestamo in datos_prestamos:
            monto_restante = float(prestamo.get('monto_restante', 0))
            with st.expander(f"📅 Préstamo {prestamo['id_prestamo']} - ${prestamo['monto_prestado']:,.2f} (Vence: {prestamo['fecha_vencimiento']})", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Propósito:** {prestamo.get('proposito', 'No especificado')}")
                with col2:
                    st.write(f"**Plazo:** {prestamo.get('plazo_meses', 0)} meses")
                with col3:
                    monto_pagado = float(prestamo.get('monto_pagado', 0))
                    st.write(f"**Pagado:** ${monto_pagado:,.2f}")
                    st.write(f"**Restante:** ${monto_restante:,.2f}")
    else:
        st.success("✅ No tiene préstamos pendientes")
    
    st.markdown("---")
    
    # Mostrar saldo neto final - CORRECCIÓN: Cálculo seguro
    st.subheader("🧮 Saldo Neto Final")
    
    # Cálculo seguro del saldo neto
    saldo_neto = float(datos_aportes['total_general']) - total_prestamos_pendientes
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**💰 Ahorro Total:** ${datos_aportes['total_general']:,.2f}")
    with col2:
        if total_prestamos_pendientes > 0:
            st.info(f"**📉 Préstamos Pendientes:** -${total_prestamos_pendientes:,.2f}")
    
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
    
    if historial_aportes and len(historial_aportes) > 0:
        # Agrupar por reunión
        reuniones = {}
        for aporte in historial_aportes:
            if aporte['id_reunion'] not in reuniones:
                reuniones[aporte['id_reunion']] = {
                    'fecha': aporte.get('fecha_reunion', 'Fecha no disponible'),
                    'aportes': []
                }
            reuniones[aporte['id_reunion']]['aportes'].append(aporte)
        
        # Mostrar por reunión
        for reunion_id, datos_reunion in reuniones.items():
            with st.expander(f"📅 Reunión del {datos_reunion['fecha']}", expanded=False):
                total_reunion = sum(float(a.get('monto', 0)) for a in datos_reunion['aportes'])
                st.write(f"**Total en esta reunión: ${total_reunion:,.2f}**")
                
                for aporte in datos_reunion['aportes']:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Tipo:** {aporte.get('tipo', 'No especificado')}")
                    with col2:
                        st.write(f"**Monto:** ${aporte.get('monto', 0):,.2f}")
                    with col3:
                        observaciones = aporte.get('observaciones')
                        if observaciones:
                            st.write(f"**Obs:** {observaciones}")
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
                    totales[tipo] = float(resultado.get('total', 0))
            
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
                'porcentaje_ahorro': porcentajes.get('porcentaje_ahorro', 0),
                'porcentaje_rifa': porcentajes.get('porcentaje_rifa', 0),
                'porcentaje_pago_prestamo': porcentajes.get('porcentaje_pagoprestamo', 0),
                'porcentaje_pago_multa': porcentajes.get('porcentaje_pagomulta', 0),
                'porcentaje_otros': porcentajes.get('porcentaje_otros', 0)
            }
            
    except Exception as e:
        st.error(f"❌ Error al obtener datos de aportes: {e}")
    
    # Retorno por defecto seguro
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
            
            return prestamos if prestamos else []
            
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
                    r.fecha as fecha_reunion
                FROM aporte a
                JOIN reunion r ON a.id_reunion = r.id_reunion
                WHERE a.id_miembro = %s
                ORDER BY r.fecha DESC, a.id_aporte DESC
            """, (id_miembro,))
            
            historial = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            return historial if historial else []
            
    except Exception as e:
        st.error(f"❌ Error al obtener historial de aportes: {e}")
    
    return []
