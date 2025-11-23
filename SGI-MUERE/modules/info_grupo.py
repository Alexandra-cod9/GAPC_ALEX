import streamlit as st
import pymysql

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

def mostrar_modulo_info_grupo():
    """Módulo de información del grupo"""
    
    # Header del módulo con botón de volver
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🏢 Información del Grupo")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Obtener información del grupo actual
    id_grupo = st.session_state.usuario.get('id_grupo', 1)
    info_grupo = obtener_informacion_grupo(id_grupo)
    
    if info_grupo:
        mostrar_informacion_existente(info_grupo, id_grupo)
    else:
        st.error("❌ No se pudo cargar la información del grupo")

def obtener_informacion_grupo(id_grupo):
    """Obtiene la información completa del grupo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            cursor.execute("""
                SELECT 
                    g.*,
                    d.nombre_distrito,
                    m.nombre_municipio,
                    dep.nombre_departamento,
                    r.texto_reglamento,
                    r.tipo_multa,
                    r.reglas_prestamo
                FROM grupo g
                LEFT JOIN distrito d ON g.id_distrito = d.id_distrito
                LEFT JOIN municipio m ON d.id_municipio = m.id_municipio
                LEFT JOIN departamento dep ON m.id_departamento = dep.id_departamento
                LEFT JOIN reglamento r ON g.id_reglamento = r.id_reglamento
                WHERE g.id_grupo = %s
            """, (id_grupo,))
            
            grupo = cursor.fetchone()
            cursor.close()
            conexion.close()
            return grupo
            
    except Exception as e:
        st.error(f"❌ Error al cargar información del grupo: {e}")
        return None

def mostrar_informacion_existente(info_grupo, id_grupo):
    """Muestra la información actual del grupo y permite editarla"""
    
    # Pestañas para organizar la información
    tab1, tab2, tab3 = st.tabs(["📋 Información General", "📜 Reglamento", "📊 Reporte de Asistencia"])
    
    with tab1:
        mostrar_informacion_general(info_grupo, id_grupo)
    
    with tab2:
        mostrar_gestion_reglamento(info_grupo, id_grupo)
    
    with tab3:
        mostrar_reporte_asistencia(id_grupo)

def mostrar_informacion_general(info_grupo, id_grupo):
    """Muestra y permite editar la información general del grupo"""
    
    st.subheader("📋 Información General del Grupo")
    
    with st.form("form_info_general"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_grupo = st.text_input(
                "🏷️ Nombre del Grupo *", 
                value=info_grupo.get('nombre_grupo', ''),
                placeholder="Ej: Grupo Solidario La Esperanza"
            )
            
            nombre_comunidad = st.text_input(
                "🏘️ Nombre de la Comunidad *", 
                value=info_grupo.get('nombre_comunidad', ''),
                placeholder="Ej: Comunidad Los Ángeles"
            )
            
            fecha_formacion = st.date_input(
                "📅 Fecha de Formación *",
                value=info_grupo.get('fecha_formacion') or datetime.now().date()
            )
            
            # Selector de frecuencia de reuniones
            frecuencia_opciones = ['semanal', 'quincenal', 'mensual']
            frecuencia_reuniones = st.selectbox(
                "🔄 Frecuencia de Reuniones *",
                options=frecuencia_opciones,
                index=frecuencia_opciones.index(info_grupo.get('frecuencia_reuniones', 'semanal'))
            )
        
        with col2:
            tasa_interes = st.number_input(
                "📈 Tasa de Interés Mensual (%) *",
                min_value=0.0,
                max_value=100.0,
                value=float(info_grupo.get('tasa_interes_mensual', 0.0)),
                step=0.1,
                format="%.2f"
            )
            
            # Selector de método de reparto
            metodo_opciones = ['proporcional', 'equitativo']
            metodo_reparto = st.selectbox(
                "💰 Método de Reparto de Utilidades *",
                options=metodo_opciones,
                index=metodo_opciones.index(info_grupo.get('metodo_reparto_utilidades', 'proporcional'))
            )
            
            meta_social = st.text_area(
                "🎯 Meta Social del Grupo",
                value=info_grupo.get('meta_social', ''),
                placeholder="Describa la meta social del grupo...",
                height=100
            )
            
            # Selector de distrito
            distrito_seleccionado = mostrar_selector_distrito(info_grupo)
        
        st.markdown("**\* Campos obligatorios**")
        
        submitted = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
        
        if submitted:
            if not nombre_grupo or not nombre_comunidad:
                st.error("❌ Por favor completa todos los campos obligatorios")
            else:
                guardar_informacion_general(
                    id_grupo, nombre_grupo, nombre_comunidad, fecha_formacion,
                    frecuencia_reuniones, tasa_interes, metodo_reparto, meta_social,
                    distrito_seleccionado
                )

def mostrar_selector_distrito(info_grupo):
    """Muestra el selector de distrito, municipio y departamento"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener todos los distritos con su municipio y departamento
            cursor.execute("""
                SELECT 
                    d.id_distrito,
                    d.nombre_distrito,
                    m.nombre_municipio,
                    dep.nombre_departamento
                FROM distrito d
                JOIN municipio m ON d.id_municipio = m.id_municipio
                JOIN departamento dep ON m.id_departamento = dep.id_departamento
                ORDER BY dep.nombre_departamento, m.nombre_municipio, d.nombre_distrito
            """)
            
            distritos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            # Crear opciones para el selectbox
            opciones = [f"{d['nombre_distrito']} - {d['nombre_municipio']} - {d['nombre_departamento']}" for d in distritos]
            
            # Encontrar el índice del distrito actual
            indice_actual = 0
            if info_grupo.get('id_distrito'):
                for i, distrito in enumerate(distritos):
                    if distrito['id_distrito'] == info_grupo['id_distrito']:
                        indice_actual = i
                        break
            
            distrito_seleccionado = st.selectbox(
                "🗺️ Distrito *",
                options=opciones,
                index=indice_actual
            )
            
            # Devolver el ID del distrito seleccionado
            if distrito_seleccionado:
                indice_seleccionado = opciones.index(distrito_seleccionado)
                return distritos[indice_seleccionado]['id_distrito']
                
    except Exception as e:
        st.error(f"❌ Error al cargar distritos: {e}")
    
    return info_grupo.get('id_distrito')

def guardar_informacion_general(id_grupo, nombre_grupo, nombre_comunidad, fecha_formacion,
                               frecuencia_reuniones, tasa_interes, metodo_reparto, meta_social, id_distrito):
    """Guarda la información general del grupo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            cursor.execute("""
                UPDATE grupo 
                SET nombre_grupo = %s,
                    nombre_comunidad = %s,
                    fecha_formacion = %s,
                    frecuencia_reuniones = %s,
                    tasa_interes_mensual = %s,
                    metodo_reparto_utilidades = %s,
                    meta_social = %s,
                    id_distrito = %s
                WHERE id_grupo = %s
            """, (nombre_grupo, nombre_comunidad, fecha_formacion, frecuencia_reuniones,
                  tasa_interes, metodo_reparto, meta_social, id_distrito, id_grupo))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("✅ Información del grupo actualizada exitosamente!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error al actualizar información: {e}")

def mostrar_gestion_reglamento(info_grupo, id_grupo):
    """Muestra la gestión del reglamento del grupo"""
    
    st.subheader("📜 Gestión del Reglamento")
    
    # Verificar si ya existe un reglamento
    id_reglamento = info_grupo.get('id_reglamento')
    
    if id_reglamento:
        st.success("✅ El grupo ya tiene un reglamento registrado")
        
        # Mostrar reglamento actual
        with st.expander("📋 Ver Reglamento Actual", expanded=True):
            if info_grupo.get('texto_reglamento'):
                st.write("**Reglamento General:**")
                st.info(info_grupo['texto_reglamento'])
            
            if info_grupo.get('tipo_multa'):
                st.write("**Tipos de Multa:**")
                st.info(info_grupo['tipo_multa'])
            
            if info_grupo.get('reglas_prestamo'):
                st.write("**Reglas de Préstamo:**")
                st.info(info_grupo['reglas_prestamo'])
    
    # Opciones para gestionar reglamento
    opcion = st.radio(
        "Selecciona una acción:",
        ["➕ Añadir Reglamento", "✏️ Editar Reglamento"] if id_reglamento else ["➕ Añadir Reglamento"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if opcion == "➕ Añadir Reglamento" or opcion == "✏️ Editar Reglamento":
        mostrar_formulario_reglamento(info_grupo, id_grupo, id_reglamento)

def mostrar_formulario_reglamento(info_grupo, id_grupo, id_reglamento=None):
    """Muestra el formulario para añadir/editar reglamento"""
    
    st.subheader("📝 Formulario de Reglamento")
    
    with st.form("form_reglamento"):
        texto_reglamento = st.text_area(
            "📜 Reglamento General *",
            value=info_grupo.get('texto_reglamento', '') if id_reglamento else '',
            placeholder="Establezca las reglas generales del grupo...",
            height=150
        )
        
        tipo_multa = st.text_area(
            "⚠️ Tipos de Multa *",
            value=info_grupo.get('tipo_multa', '') if id_reglamento else '',
            placeholder="Describa los tipos de multa y sus montos...",
            height=120
        )
        
        reglas_prestamo = st.text_area(
            "💳 Reglas de Préstamo *",
            value=info_grupo.get('reglas_prestamo', '') if id_reglamento else '',
            placeholder="Establezca las reglas para solicitar y pagar préstamos...",
            height=120
        )
        
        submitted = st.form_submit_button(
            "💾 Guardar Reglamento" if id_reglamento else "➕ Crear Reglamento", 
            use_container_width=True
        )
        
        if submitted:
            if not texto_reglamento or not tipo_multa or not reglas_prestamo:
                st.error("❌ Por favor completa todos los campos del reglamento")
            else:
                guardar_reglamento(id_grupo, texto_reglamento, tipo_multa, reglas_prestamo, id_reglamento)

def guardar_reglamento(id_grupo, texto_reglamento, tipo_multa, reglas_prestamo, id_reglamento=None):
    """Guarda o actualiza el reglamento del grupo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            if id_reglamento:
                # Actualizar reglamento existente
                cursor.execute("""
                    UPDATE reglamento 
                    SET texto_reglamento = %s,
                        tipo_multa = %s,
                        reglas_prestamo = %s
                    WHERE id_reglamento = %s
                """, (texto_reglamento, tipo_multa, reglas_prestamo, id_reglamento))
            else:
                # Insertar nuevo reglamento
                cursor.execute("""
                    INSERT INTO reglamento (texto_reglamento, tipo_multa, reglas_prestamo)
                    VALUES (%s, %s, %s)
                """, (texto_reglamento, tipo_multa, reglas_prestamo))
                
                # Obtener el ID del nuevo reglamento
                id_nuevo_reglamento = cursor.lastrowid
                
                # Actualizar el grupo con el nuevo reglamento
                cursor.execute("""
                    UPDATE grupo 
                    SET id_reglamento = %s 
                    WHERE id_grupo = %s
                """, (id_nuevo_reglamento, id_grupo))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            st.success("✅ Reglamento guardado exitosamente!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error al guardar reglamento: {e}")

def mostrar_reporte_asistencia(id_grupo):
    """Genera y muestra el reporte de asistencia para el módulo de reportes"""
    
    st.subheader("📊 Reporte de Asistencia")
    st.info("📈 Este reporte se enviará al módulo de Reportes")
    
    # Obtener datos de asistencia
    datos_asistencia = obtener_datos_asistencia(id_grupo)
    
    if datos_asistencia:
        # Mostrar resumen
        col1, col2, col3, col4 = st.columns(4)
        
        total_reuniones = len(datos_asistencia['reuniones'])
        total_asistencias = sum(len(r['asistentes']) for r in datos_asistencia['reuniones'])
        total_ausencias = sum(len(r['ausentes']) for r in datos_asistencia['reuniones'])
        tasa_asistencia = (total_asistencias / (total_asistencias + total_ausencias)) * 100 if (total_asistencias + total_ausencias) > 0 else 0
        
        with col1:
            st.metric("Total Reuniones", total_reuniones)
        with col2:
            st.metric("Total Asistencias", total_asistencias)
        with col3:
            st.metric("Total Ausencias", total_ausencias)
        with col4:
            st.metric("Tasa de Asistencia", f"{tasa_asistencia:.1f}%")
        
        # Mostrar detalles por reunión
        st.markdown("---")
        st.write("**Detalles por Reunión:**")
        
        for reunion in datos_asistencia['reuniones']:
            with st.expander(f"📅 Reunión {reunion['fecha']} - {reunion['hora']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**✅ Asistentes:**")
                    for asistente in reunion['asistentes']:
                        st.write(f"• {asistente}")
                
                with col2:
                    st.write("**❌ Ausentes:**")
                    for ausente in reunion['ausentes']:
                        st.write(f"• {ausente}")
        
        # Botón para enviar a reportes
        if st.button("📤 Enviar Reporte al Módulo de Reportes", use_container_width=True):
            guardar_reporte_asistencia(id_grupo, datos_asistencia)
            st.session_state.modulo_actual = 'reportes'
            st.success("✅ Reporte enviado al módulo de Reportes!")
            st.rerun()
    
    else:
        st.info("📝 No hay datos de asistencia para mostrar")

def obtener_datos_asistencia(id_grupo):
    """Obtiene los datos de asistencia del grupo"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # Obtener reuniones del grupo
            cursor.execute("""
                SELECT r.id_reunion, r.fecha, r.hora
                FROM reunion r
                WHERE r.id_gruppo = %s
                ORDER BY r.fecha DESC
            """, (id_grupo,))
            
            reuniones = cursor.fetchall()
            
            datos_reuniones = []
            
            for reunion in reuniones:
                # Obtener asistentes y ausentes por reunión
                cursor.execute("""
                    SELECT m.nombre, a.estado
                    FROM asistencia a
                    JOIN miembrogapc m ON a.id_miembro = m.id_miembro
                    WHERE a.id_reunion = %s
                """, (reunion['id_reunion'],))
                
                asistencias = cursor.fetchall()
                
                asistentes = [a['nombre'] for a in asistencias if a['estado'] == 'presente']
                ausentes = [a['nombre'] for a in asistencias if a['estado'] == 'ausente']
                
                datos_reuniones.append({
                    'fecha': reunion['fecha'].strftime('%d/%m/%Y'),
                    'hora': str(reunion['hora']),
                    'asistentes': asistentes,
                    'ausentes': ausentes
                })
            
            cursor.close()
            conexion.close()
            
            return {
                'reuniones': datos_reuniones,
                'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            
    except Exception as e:
        st.error(f"❌ Error al obtener datos de asistencia: {e}")
        return None

def guardar_reporte_asistencia(id_grupo, datos_asistencia):
    """Guarda el reporte de asistencia para uso en el módulo de reportes"""
    # Aquí podrías guardar en una tabla de reportes o en session_state
    if 'reportes_guardados' not in st.session_state:
        st.session_state.reportes_guardados = {}
    
    st.session_state.reportes_guardados['asistencia'] = {
        'id_grupo': id_grupo,
        'tipo': 'asistencia',
        'datos': datos_asistencia,
        'fecha_creacion': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
