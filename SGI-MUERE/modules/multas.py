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
    """Módulo especializado de multas - Vista y gestión"""
    
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
        ["📋 Ver Todas las Multas", "➕ Nueva Multa", "⚠️ Multas Activas", "✅ Multas Pagadas"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "📋 Ver Todas las Multas":
        mostrar_todas_multas()
    elif opcion == "➕ Nueva Multa":
        mostrar_nueva_multa_individual()
    elif opcion == "⚠️ Multas Activas":
        mostrar_multas_activas()
    elif opcion == "✅ Multas Pagadas":
        mostrar_multas_pagadas()

def mostrar_todas_multas():
    """Muestra todas las multas con filtros"""
    st.subheader("📋 Todas las Multas")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener todas las multas del grupo
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
                    ), 0)) as saldo_pendiente,
                    DATEDIFF(CURDATE(), mt.fecha_creacion) as dias_transcurridos
                FROM multa mt
                JOIN miembrogapc m ON mt.id_miembro = m.id_miembro
                JOIN estado e ON mt.id_estado = e.id_estado
                LEFT JOIN aporte a ON mt.id_miembro = a.id_miembro AND a.tipo = 'PagoMulta'
                WHERE m.id_grupo = %s
                GROUP BY mt.id_multa, m.nombre, mt.motivo, mt.monto, mt.fecha_creacion, e.nombre_estado
                ORDER BY mt.fecha_creacion DESC
            """, (id_grupo,))
            
            multas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas:
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    estados = ["Todos"] + list(set(m['estado'] for m in multas))
                    estado_filtro = st.selectbox("🔍 Filtrar por estado:", estados)
                
                with col2:
                    miembros = ["Todos"] + list(set(m['miembro'] for m in multas))
                    miembro_filtro = st.selectbox("👤 Filtrar por miembro:", miembros)
                
                # Aplicar filtros
                multas_filtradas = multas
                if estado_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['estado'] == estado_filtro]
                if miembro_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['miembro'] == miembro_filtro]
                
                # Estadísticas
                total_multas = len(multas_filtradas)
                total_monto = sum(m['monto'] for m in multas_filtradas)
                total_pendiente = sum(m['saldo_pendiente'] for m in multas_filtradas)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Multas", total_multas)
                with col2:
                    st.metric("💰 Total Monto", f"${total_monto:,.2f}")
                with col3:
                    st.metric("📉 Total Pendiente", f"${total_pendiente:,.2f}")
                with col4:
                    porcentaje_pagado = ((total_monto - total_pendiente) / total_monto * 100) if total_monto > 0 else 0
                    st.metric("📈 % Pagado", f"{porcentaje_pagado:.1f}%")
                
                st.markdown("---")
                
                # Mostrar multas
                for multa in multas_filtradas:
                    # Determinar icono según estado
                    if multa['estado'] == 'pagado':
                        icono = "✅"
                    elif multa['estado'] == 'mora':
                        icono = "🔴"
                    else:
                        icono = "⚠️"
                    
                    with st.expander(f"{icono} #{multa['id_multa']} - {multa['miembro']} - ${multa['monto']:,.2f} - {multa['estado']}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**📝 Motivo:** {multa['motivo']}")
                            st.write(f"**📅 Fecha:** {multa['fecha_creacion']}")
                        
                        with col2:
                            st.write(f"**💰 Monto Original:** ${multa['monto']:,.2f}")
                            st.write(f"**💵 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📉 Saldo Pendiente:** ${multa['saldo_pendiente']:,.2
