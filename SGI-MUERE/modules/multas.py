def mostrar_modulo_multas():
    """Módulo especializado de multas - Vista y gestión"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# ⚖️ Módulo de Multas")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Menú de opciones
    opcion = st.radio(
        "Selecciona una acción:",
        ["📋 Ver Todas las Multas", "➕ Nueva Multa", "⏳ Multas Pendientes", "✅ Multas Pagadas"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "📋 Ver Todas las Multas":
        mostrar_todas_multas()
    elif opcion == "➕ Nueva Multa":
        mostrar_nueva_multa()
    elif opcion == "⏳ Multas Pendientes":
        mostrar_multas_pendientes()
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
                    m.id_multa,
                    mb.nombre as miembro,
                    m.motivo,
                    m.monto,
                    m.fecha_multa,
                    m.fecha_vencimiento,
                    m.estado,
                    m.descripcion,
                    DATEDIFF(m.fecha_vencimiento, CURDATE()) as dias_restantes,
                    CASE 
                        WHEN m.estado = 'pagada' THEN 'Pagada'
                        WHEN DATEDIFF(m.fecha_vencimiento, CURDATE()) < 0 THEN 'Vencida'
                        WHEN DATEDIFF(m.fecha_vencimiento, CURDATE()) <= 7 THEN 'Por vencer'
                        ELSE 'En tiempo'
                    END as situacion
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                WHERE mb.id_grupo = %s
                ORDER BY m.estado, m.fecha_vencimiento DESC
            """, (id_grupo,))
            
            multas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas:
                # Filtros
                col1, col2, col3 = st.columns(3)
                with col1:
                    estados = ["Todos"] + list(set(m['estado'] for m in multas))
                    estado_filtro = st.selectbox("🔍 Filtrar por estado:", estados)
                
                with col2:
                    miembros = ["Todos"] + list(set(m['miembro'] for m in multas))
                    miembro_filtro = st.selectbox("👤 Filtrar por miembro:", miembros)
                
                with col3:
                    situaciones = ["Todas", "En tiempo", "Por vencer", "Vencida", "Pagada"]
                    situacion_filtro = st.selectbox("📅 Filtrar por situación:", situaciones)
                
                # Aplicar filtros
                multas_filtradas = multas
                if estado_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['estado'] == estado_filtro]
                if miembro_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['miembro'] == miembro_filtro]
                if situacion_filtro != "Todas":
                    if situacion_filtro == "Vencida":
                        multas_filtradas = [m for m in multas_filtradas if m['dias_restantes'] < 0 and m['estado'] != 'pagada']
                    elif situacion_filtro == "Por vencer":
                        multas_filtradas = [m for m in multas_filtradas if 0 <= m['dias_restantes'] <= 7 and m['estado'] != 'pagada']
                    elif situacion_filtro == "En tiempo":
                        multas_filtradas = [m for m in multas_filtradas if m['dias_restantes'] > 7 and m['estado'] != 'pagada']
                    elif situacion_filtro == "Pagada":
                        multas_filtradas = [m for m in multas_filtradas if m['estado'] == 'pagada']
                
                # Estadísticas
                total_multas = len(multas_filtradas)
                total_pendiente = sum(m['monto'] for m in multas_filtradas if m['estado'] != 'pagada')
                total_pagado = sum(m['monto'] for m in multas_filtradas if m['estado'] == 'pagada')
                multas_vencidas = len([m for m in multas_filtradas if m['dias_restantes'] < 0 and m['estado'] != 'pagada'])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Multas", total_multas)
                with col2:
                    st.metric("💰 Total Pendiente", f"${total_pendiente:,.2f}")
                with col3:
                    st.metric("✅ Total Pagado", f"${total_pagado:,.2f}")
                with col4:
                    st.metric("⚠️ Multas Vencidas", multas_vencidas)
                
                st.markdown("---")
                
                # Mostrar multas
                for multa in multas_filtradas:
                    # Determinar color según situación
                    if multa['estado'] == 'pagada':
                        color = "✅"
                        situacion_texto = "PAGADA"
                    elif multa['dias_restantes'] < 0:
                        color = "🔴"
                        situacion_texto = f"VENCIDA (-{abs(multa['dias_restantes'])} días)"
                    elif multa['dias_restantes'] <= 7:
                        color = "🟡"
                        situacion_texto = f"Por vencer ({multa['dias_restantes']} días)"
                    else:
                        color = "🟢"
                        situacion_texto = f"En tiempo ({multa['dias_restantes']} días)"
                    
                    with st.expander(f"{color} #{multa['id_multa']} - {multa['miembro']} - ${multa['monto']:,.2f} - {multa['estado']}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**💰 Monto:** ${multa['monto']:,.2f}")
                            st.write(f"**📅 Fecha Multa:** {multa['fecha_multa']}")
                        
                        with col2:
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                            st.write(f"**📅 Fecha Vencimiento:** {multa['fecha_vencimiento']}")
                            st.write(f"**⏱️ Días Restantes:** {multa['dias_restantes']}")
                        
                        with col3:
                            st.write(f"**🔒 Estado:** {multa['estado']}")
                            st.write(f"**📊 Situación:** {situacion_texto}")
                            if multa['descripcion']:
                                st.write(f"**📝 Descripción:** {multa['descripcion']}")
                            
                            # Botón para marcar como pagada
                            if multa['estado'] == 'pendiente':
                                if st.button("✅ Marcar como Pagada", key=f"pagar_{multa['id_multa']}"):
                                    marcar_multa_pagada(multa['id_multa'])
                                    st.rerun()
            else:
                st.info("📝 No hay multas registradas en este grupo.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas: {e}")

def mostrar_nueva_multa():
    """Formulario para registrar nueva multa"""
    st.subheader("➕ Nueva Multa")
    
    st.info("""
    **💡 Información:**
    Al registrar una multa aquí, se afecta automáticamente el saldo del miembro:
    - Se crea la multa con estado 'pendiente'
    - El miembro deberá pagar la multa antes de la fecha de vencimiento
    - La multa afecta el estado financiero del miembro
    """)
    
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
                st.info(f"**📧 Teléfono:** {miembro_seleccionado['telefono']}")
            
            # Datos de la multa
            st.subheader("📝 Datos de la Multa")
            
            col1, col2 = st.columns(2)
            
            with col1:
                motivo = st.selectbox(
                    "📋 Motivo de la multa:",
                    ["Falta a reunión", "Llegada tarde", "Incumplimiento de pago", "Otro"]
                )
                
                if motivo == "Otro":
                    motivo_personalizado = st.text_input("📝 Especificar motivo:")
                    motivo_final = motivo_personalizado if motivo_personalizado else "Otro"
                else:
                    motivo_final = motivo
                
                monto_multa = st.number_input(
                    "💰 Monto de la multa:",
                    min_value=0.0,
                    value=50.0,
                    step=10.0
                )
            
            with col2:
                fecha_multa = st.date_input(
                    "📅 Fecha de la multa:",
                    value=datetime.now()
                )
                
                fecha_vencimiento = st.date_input(
                    "⏰ Fecha de vencimiento:",
                    value=datetime.now() + relativedelta(days=7)
                )
            
            descripcion = st.text_area(
                "📄 Descripción detallada:",
                placeholder="Describe los detalles de la infracción cometida...",
                height=100
            )
            
            # Resumen
            if monto_multa > 0:
                st.markdown("---")
                st.subheader("🧮 Resumen de la Multa")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("👤 Miembro", miembro_seleccionado['nombre'])
                
                with col2:
                    st.metric("💰 Monto", f"${monto_multa:,.2f}")
                
                with col3:
                    dias_vencimiento = (fecha_vencimiento - fecha_multa).days
                    st.metric("⏱️ Plazo para pagar", f"{dias_vencimiento} días")
                
                st.info(f"""
                **📊 Detalles:**
                - **Motivo:** {motivo_final}
                - **Monto:** ${monto_multa:,.2f}
                - **Fecha multa:** {fecha_multa.strftime('%d/%m/%Y')}
                - **Vencimiento:** {fecha_vencimiento.strftime('%d/%m/%Y')}
                - **Estado:** Pendiente
                """)
            
            # Botón de envío
            submitted = st.form_submit_button(
                "⚖️ Registrar Multa", 
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                if monto_multa > 0 and motivo_final:
                    guardar_multa(
                        miembro_seleccionado, 
                        motivo_final, 
                        monto_multa, 
                        fecha_multa, 
                        fecha_vencimiento, 
                        descripcion
                    )
                else:
                    st.error("❌ Completa todos los campos obligatorios")
        else:
            st.warning("👤 Selecciona un miembro para continuar")

def buscar_miembro_multa():
    """Busca y selecciona un miembro para multa"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener todos los miembros del grupo
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
                opciones = ["Selecciona un miembro"] + [f"{m['id_miembro']} - {m['nombre']}" for m in miembros]
                
                miembro_seleccionado_opcion = st.selectbox(
                    "👤 Selecciona el miembro a multar:",
                    opciones,
                    key="selector_miembro_multa"
                )
                
                if miembro_seleccionado_opcion and miembro_seleccionado_opcion != "Selecciona un miembro":
                    # Extraer ID del miembro seleccionado
                    miembro_id = int(miembro_seleccionado_opcion.split(" - ")[0])
                    miembro_info = next((m for m in miembros if m['id_miembro'] == miembro_id), None)
                    return miembro_info
            else:
                st.info("📝 No hay miembros en este grupo.")
                return None
                
    except Exception as e:
        st.error(f"❌ Error al cargar miembros: {e}")
    
    return None

def guardar_multa(miembro, motivo, monto, fecha_multa, fecha_vencimiento, descripcion):
    """Guarda una nueva multa en la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Insertar multa
            cursor.execute("""
                INSERT INTO multa (
                    id_miembro, motivo, monto, fecha_multa, 
                    fecha_vencimiento, descripcion, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                miembro['id_miembro'],
                motivo,
                monto,
                fecha_multa,
                fecha_vencimiento,
                descripcion,
                'pendiente'
            ))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("🎉 ¡Multa registrada exitosamente!")
            st.balloons()
            
            # Mostrar resumen
            st.info(f"""
            **📋 Resumen de la Multa:**
            - **Miembro:** {miembro['nombre']}
            - **Motivo:** {motivo}
            - **Monto:** ${monto:,.2f}
            - **Fecha Multa:** {fecha_multa.strftime('%d/%m/%Y')}
            - **Vencimiento:** {fecha_vencimiento.strftime('%d/%m/%Y')}
            - **Estado:** Pendiente
            """)
            
    except Exception as e:
        st.error(f"❌ Error al registrar multa: {e}")

def mostrar_multas_pendientes():
    """Muestra solo las multas pendientes de pago"""
    st.subheader("⏳ Multas Pendientes")
    
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
                    m.motivo,
                    m.monto,
                    m.fecha_multa,
                    m.fecha_vencimiento,
                    m.descripcion,
                    DATEDIFF(m.fecha_vencimiento, CURDATE()) as dias_restantes,
                    CASE 
                        WHEN DATEDIFF(m.fecha_vencimiento, CURDATE()) < 0 THEN 'Vencida'
                        WHEN DATEDIFF(m.fecha_vencimiento, CURDATE()) <= 7 THEN 'Por vencer'
                        ELSE 'En tiempo'
                    END as situacion
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                WHERE mb.id_grupo = %s AND m.estado = 'pendiente'
                ORDER BY m.fecha_vencimiento ASC
            """, (id_grupo,))
            
            multas_pendientes = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas_pendientes:
                # Estadísticas
                total_pendientes = len(multas_pendientes)
                total_monto_pendiente = sum(m['monto'] for m in multas_pendientes)
                multas_vencidas = len([m for m in multas_pendientes if m['dias_restantes'] < 0])
                multas_por_vencer = len([m for m in multas_pendientes if 0 <= m['dias_restantes'] <= 7])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Multas Pendientes", total_pendientes)
                with col2:
                    st.metric("💰 Total Pendiente", f"${total_monto_pendiente:,.2f}")
                with col3:
                    st.metric("⚠️ Vencidas", multas_vencidas)
                with col4:
                    st.metric("🟡 Por vencer", multas_por_vencer)
                
                st.markdown("---")
                
                for multa in multas_pendientes:
                    # Determinar color según situación
                    if multa['dias_restantes'] < 0:
                        color = "🔴"
                        situacion_texto = f"VENCIDA (-{abs(multa['dias_restantes'])} días)"
                    elif multa['dias_restantes'] <= 7:
                        color = "🟡"
                        situacion_texto = f"Por vencer ({multa['dias_restantes']} días)"
                    else:
                        color = "🟢"
                        situacion_texto = f"En tiempo ({multa['dias_restantes']} días)"
                    
                    with st.expander(f"{color} {multa['miembro']} - ${multa['monto']:,.2f} - {situacion_texto}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**💰 Monto:** ${multa['monto']:,.2f}")
                            st.write(f"**📅 Fecha Multa:** {multa['fecha_multa']}")
                        with col2:
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                            st.write(f"**📅 Fecha Vencimiento:** {multa['fecha_vencimiento']}")
                            st.write(f"**⏱️ Días Restantes:** {multa['dias_restantes']}")
                        with col3:
                            if multa['descripcion']:
                                st.write(f"**📝 Descripción:** {multa['descripcion']}")
                            
                            # Botón para marcar como pagada
                            if st.button("✅ Marcar como Pagada", key=f"pagar_pend_{multa['id_multa']}"):
                                marcar_multa_pagada(multa['id_multa'])
                                st.rerun()
            else:
                st.success("✅ No hay multas pendientes en este momento.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas pendientes: {e}")

def mostrar_multas_pagadas():
    """Muestra las multas que han sido pagadas"""
    st.subheader("✅ Multas Pagadas")
    
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            id_grupo = st.session_state.usuario.get('id_grupo', 1)
            
            # Obtener multas pagadas
            cursor.execute("""
                SELECT 
                    m.id_multa,
                    mb.nombre as miembro,
                    m.motivo,
                    m.monto,
                    m.fecha_multa,
                    m.fecha_vencimiento,
                    m.descripcion,
                    m.fecha_pago
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                WHERE mb.id_grupo = %s AND m.estado = 'pagada'
                ORDER BY m.fecha_pago DESC
            """, (id_grupo,))
            
            multas_pagadas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas_pagadas:
                st.info(f"📊 Se encontraron {len(multas_pagadas)} multas pagadas")
                
                total_recaudado = sum(m['monto'] for m in multas_pagadas)
                st.metric("💰 Total Recaudado por Multas", f"${total_recaudado:,.2f}")
                
                st.markdown("---")
                
                for multa in multas_pagadas:
                    with st.expander(f"✅ #{multa['id_multa']} - {multa['miembro']} - ${multa['monto']:,.2f}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**💰 Monto:** ${multa['monto']:,.2f}")
                            st.write(f"**📅 Fecha Multa:** {multa['fecha_multa']}")
                        with col2:
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                            st.write(f"**📅 Fecha Vencimiento:** {multa['fecha_vencimiento']}")
                            st.write(f"**📅 Fecha Pago:** {multa['fecha_pago']}")
                        if multa['descripcion']:
                            st.write(f"**📝 Descripción:** {multa['descripcion']}")
            else:
                st.info("📝 No hay multas pagadas.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas pagadas: {e}")

def marcar_multa_pagada(id_multa):
    """Marca una multa como pagada y actualiza el estado"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Actualizar multa a estado 'pagada' y establecer fecha de pago
            cursor.execute("""
                UPDATE multa 
                SET estado = 'pagada', fecha_pago = CURDATE()
                WHERE id_multa = %s
            """, (id_multa,))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("✅ Multa marcada como pagada exitosamente")
            
    except Exception as e:
        st.error(f"❌ Error al actualizar multa: {e}")
