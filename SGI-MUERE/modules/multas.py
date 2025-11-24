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
        mostrar_nueva_multa_individual()
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
                    e.nombre_estado as estado,
                    m.fecha_creacion,
                    COALESCE(SUM(a.monto), 0) as total_pagado,
                    (m.monto - COALESCE(SUM(a.monto), 0)) as saldo_pendiente,
                    DATEDIFF(CURDATE(), m.fecha_creacion) as dias_transcurridos
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                JOIN estado e ON m.id_estado = e.id_estado
                LEFT JOIN aporte a ON m.id_multa = a.id_multa AND a.tipo = 'PagoMulta'
                WHERE mb.id_grupo = %s
                GROUP BY m.id_multa, mb.nombre, m.motivo, m.monto, e.nombre_estado, m.fecha_creacion
                ORDER BY e.nombre_estado, m.fecha_creacion DESC
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
                    situacion = ["Todas", "Pendientes", "Pagadas", "En mora"]
                    situacion_filtro = st.selectbox("📅 Filtrar por situación:", situacion)
                
                # Aplicar filtros
                multas_filtradas = multas
                if estado_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['estado'] == estado_filtro]
                if miembro_filtro != "Todos":
                    multas_filtradas = [m for m in multas_filtradas if m['miembro'] == miembro_filtro]
                if situacion_filtro != "Todas":
                    if situacion_filtro == "Pendientes":
                        multas_filtradas = [m for m in multas_filtradas if m['saldo_pendiente'] > 0]
                    elif situacion_filtro == "Pagadas":
                        multas_filtradas = [m for m in multas_filtradas if m['saldo_pendiente'] <= 0]
                    elif situacion_filtro == "En mora":
                        multas_filtradas = [m for m in multas_filtradas if m['dias_transcurridos'] > 30 and m['saldo_pendiente'] > 0]
                
                # Estadísticas
                total_multas = len(multas_filtradas)
                total_pendiente = sum(m['saldo_pendiente'] for m in multas_filtradas)
                total_recaudado = sum(m['total_pagado'] for m in multas_filtradas)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Multas", total_multas)
                with col2:
                    st.metric("💰 Total Recaudado", f"${total_recaudado:,.2f}")
                with col3:
                    st.metric("📉 Total Pendiente", f"${total_pendiente:,.2f}")
                with col4:
                    multas_mora = len([m for m in multas_filtradas if m['dias_transcurridos'] > 30 and m['saldo_pendiente'] > 0])
                    st.metric("⚠️ En Mora", multas_mora)
                
                st.markdown("---")
                
                # Mostrar multas
                for multa in multas_filtradas:
                    # Determinar color según situación
                    if multa['saldo_pendiente'] <= 0:
                        color = "🟢"  # Pagada
                        situacion_texto = "PAGADA"
                    elif multa['dias_transcurridos'] > 30:
                        color = "🔴"  # En mora
                        situacion_texto = f"EN MORA ({multa['dias_transcurridos']} días)"
                    else:
                        color = "🟡"  # Pendiente
                        situacion_texto = f"PENDIENTE ({multa['dias_transcurridos']} días)"
                    
                    with st.expander(f"{color} #{multa['id_multa']} - {multa['miembro']} - ${multa['monto']:,.2f} - {multa['estado']}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**💵 Monto Total:** ${multa['monto']:,.2f}")
                            st.write(f"**📅 Fecha Creación:** {multa['fecha_creacion']}")
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                        
                        with col2:
                            st.write(f"**💰 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📉 Saldo Pendiente:** ${multa['saldo_pendiente']:,.2f}")
                            st.write(f"**📅 Días Transcurridos:** {multa['dias_transcurridos']}")
                            st.write(f"**🔒 Estado:** {multa['estado']}")
                        
                        with col3:
                            st.write(f"**📊 Situación:** {situacion_texto}")
                            
                            # Botón para registrar pago
                            if multa['saldo_pendiente'] > 0:
                                if st.button("💳 Registrar Pago", key=f"pago_multa_{multa['id_multa']}"):
                                    registrar_pago_multa(multa['id_multa'])
                            
                            # Botón para cambiar estado
                            if st.button("🔄 Cambiar Estado", key=f"estado_{multa['id_multa']}"):
                                cambiar_estado_multa(multa['id_multa'])
            else:
                st.info("📝 No hay multas registradas en este grupo.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas: {e}")

def mostrar_nueva_multa_individual():
    """Formulario para nueva multa fuera de reunión"""
    st.subheader("➕ Nueva Multa")
    
    st.info("""
    **💡 Información:**
    Al registrar una multa aquí, se simula lo que pasaría en una reunión:
    - Se crea la multa con estado 'activo'
    - Se afecta el saldo neto del miembro automáticamente
    - La multa queda lista para seguimiento
    """)
    
    with st.form("form_nueva_multa_individual"):
        # Buscar miembro
        miembro_seleccionado = buscar_miembro_multa()
        
        miembro_valido = False
        form_content_ready = False
        
        if miembro_seleccionado:
            st.markdown("---")
            
            # Mostrar información del miembro
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**👤 Miembro:** {miembro_seleccionado['nombre']}")
            with col2:
                st.info(f"**💰 Ahorro Actual:** ${miembro_seleccionado['ahorro_actual']:,.2f}")
            with col3:
                st.info(f"**📞 Teléfono:** {miembro_seleccionado['telefono']}")
            
            miembro_valido = True
            
            # Solo mostrar el formulario completo si el miembro es válido
            if miembro_valido:
                # Datos de la multa
                st.subheader("📝 Datos de la Multa")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    monto_multa = st.number_input(
                        "💵 Monto de la multa:",
                        min_value=0.0,
                        max_value=1000.0,
                        value=0.0,
                        step=10.0,
                        help="Monto de la multa a aplicar"
                    )
                    
                    motivo = st.text_area(
                        "📋 Motivo de la multa:",
                        placeholder="Describe el motivo de la multa...",
                        height=100
                    )
                
                with col2:
                    fecha_creacion = st.date_input(
                        "📅 Fecha de la multa:",
                        value=datetime.now()
                    )
                    
                    # Selector de tipo de multa común
                    tipo_multa = st.selectbox(
                        "⚖️ Tipo de infracción:",
                        [
                            "Falta de asistencia",
                            "Llegada tarde", 
                            "Incumplimiento de reglas",
                            "Pago atrasado",
                            "Otro"
                        ]
                    )
                
                # Si selecciona "Otro", mostrar campo adicional
                if tipo_multa == "Otro":
                    motivo_especifico = st.text_input(
                        "📝 Especificar motivo:",
                        placeholder="Describe específicamente la infracción..."
                    )
                    if motivo_especifico:
                        motivo = f"{tipo_multa}: {motivo_especifico}"
                
                form_content_ready = True
        
        # ✅ SIEMPRE mostrar el botón de envío, pero deshabilitado si no hay miembro válido
        if miembro_seleccionado and miembro_valido and form_content_ready:
            submitted = st.form_submit_button(
                "✅ Aplicar Multa", 
                use_container_width=True,
                type="primary"
            )
        else:
            submitted = st.form_submit_button(
                "✅ Aplicar Multa", 
                use_container_width=True,
                type="primary",
                disabled=True
            )
        
        # Validar cuando se envía el formulario
        if submitted:
            if monto_multa > 0 and motivo:
                guardar_multa_individual(
                    miembro_seleccionado, 
                    monto_multa, 
                    motivo, 
                    fecha_creacion
                )
            else:
                st.error("❌ Completa todos los campos obligatorios")

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
                    m.id_miembro,
                    m.nombre,
                    m.telefono,
                    COALESCE(SUM(a.monto), 0) as ahorro_actual
                FROM miembrogapc m
                LEFT JOIN aporte a ON m.id_miembro = a.id_miembro AND a.tipo = 'Ahorro'
                WHERE m.id_grupo = %s
                GROUP BY m.id_miembro, m.nombre, m.telefono
                ORDER BY m.nombre
            """, (id_grupo,))
            
            miembros = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if miembros:
                # Crear lista de opciones
                opciones = ["Selecciona un miembro"]
                miembros_info = {}
                
                for miembro in miembros:
                    opciones.append(f"👤 {miembro['id_miembro']} - {miembro['nombre']} (Ahorro: ${miembro['ahorro_actual']:,.2f})")
                    miembros_info[miembro['id_miembro']] = miembro
                
                miembro_seleccionado_opcion = st.selectbox(
                    "👤 Selecciona el miembro a multar:",
                    opciones,
                    key="selector_miembro_multa"
                )
                
                if miembro_seleccionado_opcion and miembro_seleccionado_opcion != "Selecciona un miembro":
                    # Extraer ID del miembro seleccionado
                    miembro_id = int(miembro_seleccionado_opcion.split(" - ")[0].replace("👤 ", ""))
                    return miembros_info.get(miembro_id)
                        
            else:
                st.info("📝 No hay miembros en este grupo.")
                return None
                
    except Exception as e:
        st.error(f"❌ Error al cargar miembros: {e}")
    
    return None

def guardar_multa_individual(miembro, monto, motivo, fecha_creacion):
    """Guarda una multa individual fuera de reunión"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener el ID del estado 'activo'
            cursor.execute("SELECT id_estado FROM estado WHERE nombre_estado = 'activo' LIMIT 1")
            estado_activo = cursor.fetchone()
            id_estado = estado_activo['id_estado'] if estado_activo else 1
            
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
                fecha_creacion
            ))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("🎉 ¡Multa aplicada exitosamente!")
            st.balloons()
            
            # Mostrar resumen
            st.info(f"""
            **📋 Resumen de la Multa:**
            - **Miembro:** {miembro['nombre']}
            - **Monto:** ${monto:,.2f}
            - **Motivo:** {motivo}
            - **Fecha:** {fecha_creacion.strftime('%d/%m/%Y')}
            - **Estado:** Activa
            """)
            
    except Exception as e:
        st.error(f"❌ Error al guardar multa: {e}")

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
                    e.nombre_estado as estado,
                    m.fecha_creacion,
                    COALESCE(SUM(a.monto), 0) as total_pagado,
                    (m.monto - COALESCE(SUM(a.monto), 0)) as saldo_pendiente,
                    DATEDIFF(CURDATE(), m.fecha_creacion) as dias_transcurridos
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                JOIN estado e ON m.id_estado = e.id_estado
                LEFT JOIN aporte a ON m.id_multa = a.id_multa AND a.tipo = 'PagoMulta'
                WHERE mb.id_grupo = %s AND e.nombre_estado = 'activo'
                GROUP BY m.id_multa, mb.nombre, m.motivo, m.monto, e.nombre_estado, m.fecha_creacion
                HAVING saldo_pendiente > 0
                ORDER BY m.fecha_creacion ASC
            """, (id_grupo,))
            
            multas_pendientes = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas_pendientes:
                # Estadísticas
                total_pendientes = len(multas_pendientes)
                total_pendiente = sum(m['saldo_pendiente'] for m in multas_pendientes)
                total_recaudado = sum(m['total_pagado'] for m in multas_pendientes)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Multas Pendientes", total_pendientes)
                with col2:
                    st.metric("💰 Total Recaudado", f"${total_recaudado:,.2f}")
                with col3:
                    st.metric("📉 Total Pendiente", f"${total_pendiente:,.2f}")
                with col4:
                    multas_mora = len([m for m in multas_pendientes if m['dias_transcurridos'] > 30])
                    st.metric("⚠️ En Mora", multas_mora)
                
                st.markdown("---")
                
                for multa in multas_pendientes:
                    # Determinar color según días transcurridos
                    if multa['dias_transcurridos'] > 30:
                        color = "🔴"  # En mora
                        estado = f"EN MORA ({multa['dias_transcurridos']} días)"
                    else:
                        color = "🟡"  # Pendiente
                        estado = f"PENDIENTE ({multa['dias_transcurridos']} días)"
                    
                    with st.expander(f"{color} {multa['miembro']} - ${multa['monto']:,.2f} - {estado}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**💵 Monto Total:** ${multa['monto']:,.2f}")
                            st.write(f"**💰 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                        with col2:
                            st.write(f"**📉 Saldo Pendiente:** ${multa['saldo_pendiente']:,.2f}")
                            st.write(f"**📅 Fecha Creación:** {multa['fecha_creacion']}")
                            st.write(f"**⏱️ Días Transcurridos:** {multa['dias_transcurridos']}")
                        with col3:
                            st.write(f"**🔒 Estado:** {multa['estado']}")
                            
                            # Botón para registrar pago
                            if st.button("💳 Registrar Pago", key=f"pago_pen_{multa['id_multa']}"):
                                registrar_pago_multa(multa['id_multa'])
            else:
                st.success("✅ No hay multas pendientes en este momento.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas pendientes: {e}")

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
                    m.id_multa,
                    mb.nombre as miembro,
                    m.motivo,
                    m.monto,
                    e.nombre_estado as estado,
                    m.fecha_creacion,
                    COALESCE(SUM(a.monto), 0) as total_pagado,
                    MAX(a.fecha) as fecha_ultimo_pago
                FROM multa m
                JOIN miembrogapc mb ON m.id_miembro = mb.id_miembro
                JOIN estado e ON m.id_estado = e.id_estado
                LEFT JOIN aporte a ON m.id_multa = a.id_multa AND a.tipo = 'PagoMulta'
                WHERE mb.id_grupo = %s
                GROUP BY m.id_multa, mb.nombre, m.motivo, m.monto, e.nombre_estado, m.fecha_creacion
                HAVING total_pagado >= m.monto
                ORDER BY fecha_ultimo_pago DESC
            """, (id_grupo,))
            
            multas_pagadas = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            if multas_pagadas:
                st.info(f"📊 Se encontraron {len(multas_pagadas)} multas completamente pagadas")
                
                for multa in multas_pagadas:
                    with st.expander(f"✅ #{multa['id_multa']} - {multa['miembro']} - ${multa['monto']:,.2f}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**👤 Miembro:** {multa['miembro']}")
                            st.write(f"**💵 Monto Total:** ${multa['monto']:,.2f}")
                            st.write(f"**💰 Total Pagado:** ${multa['total_pagado']:,.2f}")
                            st.write(f"**📅 Fecha Creación:** {multa['fecha_creacion']}")
                        with col2:
                            st.write(f"**📋 Motivo:** {multa['motivo']}")
                            st.write(f"**🔒 Estado:** {multa['estado']}")
                            st.write(f"**📅 Último Pago:** {multa['fecha_ultimo_pago']}")
            else:
                st.info("📝 No hay multas completamente pagadas.")
                
    except Exception as e:
        st.error(f"❌ Error al cargar multas pagadas: {e}")

def registrar_pago_multa(id_multa):
    """Registra un pago para una multa"""
    st.info("🔧 Función de registro de pago de multa en desarrollo...")
    st.session_state.registrar_pago_multa = id_multa

def cambiar_estado_multa(id_multa):
    """Cambia el estado de una multa"""
    st.info("🔧 Función de cambio de estado de multa en desarrollo...")
