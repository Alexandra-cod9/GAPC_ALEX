import streamlit as st
import pymysql

# ---------------------------
# FUNCIÓN DE CONEXIÓN A BD
# ---------------------------
def obtener_conexion():
    return pymysql.connect(
        host='bhzcn4gxgbe5tcxihqd1-mysql.services.clever-cloud.com',
        user='usv5pnvafxbrw5hs',
        password='WiOSztB38WxsKuXjnQgT',
        database='bhzcn4gxgbe5tcxihqd1',
        port=3306
    )


def mostrar_modulo_miembros():
    """Módulo de gestión de miembros"""
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 👥 Módulo de Miembros")
    with col2:
        if st.button("⬅️ Volver al Dashboard", use_container_width=True):
            st.session_state.modulo_actual = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    st.subheader("Gestión de Miembros")

    opcion = st.selectbox(
        "Selecciona una acción:",
        ["Ver lista de miembros", 
         "Buscar miembro",
         "Agregar nuevo miembro", 
         "Editar miembro", 
         "Eliminar miembro"]
    )

    # ============================================================
    # 📌 FUNCIONES DE CONSULTA
    # ============================================================
    def obtener_roles():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_rol, tipo_rol FROM rol")
        roles = cursor.fetchall()
        cursor.close()
        conexion.close()
        return roles

    def obtener_miembros():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id_miembro, nombre, telefono, dui, id_rol 
            FROM miembrogapc
            WHERE id_grupo = 1
        """)
        miembros = cursor.fetchall()
        cursor.close()
        conexion.close()
        return miembros


    # ============================================================
    # 📌 VER LISTA DE MIEMBROS
    # ============================================================
    if opcion == "Ver lista de miembros":
        st.write("📄 Lista de miembros:")

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
            SELECT 
                m.id_miembro,
                m.nombre,

                -- Ahorros
                IFNULL((SELECT SUM(a.monto)
                        FROM aporte a
                        WHERE a.id_miembro = m.id_miembro
                        AND a.tipo = 'Ahorro'),0) AS ahorro_total,

                -- Préstamos pendientes
                IFNULL((SELECT SUM(p.monto_prestado - 
                                   IFNULL((SELECT SUM(pg.monto_capital)
                                           FROM pago pg
                                           WHERE pg.id_prestamo = p.id_prestamo),0))
                        FROM prestamo p
                        WHERE p.id_miembro = m.id_miembro
                        AND p.estado = 'aprobado'),0) AS prestamos_pendientes
            FROM miembrogapc m
            WHERE m.id_grupo = 1
            """

            cursor.execute(query)
            miembros = cursor.fetchall()

            for m in miembros:
                st.markdown(f"""
                ### {m[1]}
                - 💵 **Ahorro total:** ${m[2]}
                - 🧾 **Préstamos pendientes:** ${m[3]}
                ---
                """)

        except Exception as e:
            st.error("Error al cargar datos: " + str(e))
        finally:
            cursor.close()
            conexion.close()


    # ============================================================
    # 📌 BUSCAR MIEMBRO
    # ============================================================
    elif opcion == "Buscar miembro":
        st.subheader("🔍 Buscar miembro por nombre")

        termino = st.text_input("Ingrese parte del nombre:")

        if termino:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_miembro, nombre, telefono, dui
                FROM miembrogapc
                WHERE id_grupo = 1
                AND nombre LIKE %s
            """, ("%"+termino+"%",))
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()

            for r in resultados:
                st.write(f"**{r[1]}** — Tel: {r[2]} — DUI: {r[3]}")


    # ============================================================
    # 📌 AGREGAR MIEMBRO
    # ============================================================
    elif opcion == "Agregar nuevo miembro":
        st.subheader("➕ Agregar Nuevo Miembro")

        ROLES_VALIDOS = ["Secretaria", "Presidente", "Tesorera", "llave", "socio"]

        rol_texto = st.selectbox("Rol", ROLES_VALIDOS)

        nombre = st.text_input("Nombre completo")
        telefono = st.text_input("Teléfono")
        dui = st.text_input("DUI")

        correo = st.text_input("Correo (solo para Secretaria o Presidente)")
        contrasena = st.text_input("Contraseña (solo para Secretaria o Presidente)", type="password")

        requiere_credenciales = rol_texto in ["Secretaria", "Presidente"]

        if st.button("Guardar miembro"):
            if not nombre or not telefono or not dui:
                st.error("Los campos nombre, teléfono y DUI son obligatorios.")
                return
            
            if requiere_credenciales and (not correo or not contrasena):
                st.error("Correo y contraseña son obligatorios para este rol.")
                return

            try:
                conexion = obtener_conexion()
                cursor = conexion.cursor()

                cursor.execute("SELECT id_rol FROM rol WHERE tipo_rol=%s", (rol_texto,))
                id_rol = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO miembrogapc (nombre, telefono, dui, id_grupo, id_rol, correo, contrasena)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    nombre, telefono, dui, 1, id_rol,
                    correo if requiere_credenciales else None,
                    contrasena if requiere_credenciales else None
                ))

                conexion.commit()
                st.success("Miembro agregado correctamente.")

            except Exception as e:
                st.error("Error al guardar: " + str(e))

            finally:
                cursor.close()
                conexion.close()


    # ============================================================
    # 📌 EDITAR MIEMBRO
    # ============================================================
    elif opcion == "Editar miembro":
        st.subheader("✏️ Editar datos de un miembro")

        miembros = obtener_miembros()
        lista = {f"{m[1]} (DUI {m[3]})": m[0] for m in miembros}

        seleccionado = st.selectbox("Seleccione un miembro:", list(lista.keys()))
        id_miembro = lista[seleccionado]

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT nombre, telefono, dui, id_rol, correo, contrasena 
            FROM miembrogapc WHERE id_miembro=%s
        """, (id_miembro,))
        datos = cursor.fetchone()

        nombre = st.text_input("Nombre", datos[0])
        telefono = st.text_input("Teléfono", datos[1])
        dui = st.text_input("DUI", datos[2])

        # obtener roles del sistema
        roles = obtener_roles()
        roles_dict = {r[1]: r[0] for r in roles}
        rol_actual = [k for k,v in roles_dict.items() if v == datos[3]][0]

        rol = st.selectbox("Rol", list(roles_dict.keys()), index=list(roles_dict.keys()).index(rol_actual))

        correo = st.text_input("Correo", datos[4] if datos[4] else "")
        contrasena = st.text_input("Contraseña", datos[5] if datos[5] else "", type="password")

        if st.button("Actualizar"):
            cursor.execute("""
                UPDATE miembrogapc
                SET nombre=%s, telefono=%s, dui=%s, id_rol=%s, correo=%s, contrasena=%s
                WHERE id_miembro=%s
            """, (nombre, telefono, dui, roles_dict[rol], correo, contrasena, id_miembro))

            conexion.commit()
            st.success("Miembro actualizado correctamente.")

        cursor.close()
        conexion.close()


    # ============================================================
    # 📌 ELIMINAR MIEMBRO
    # ============================================================
    elif opcion == "Eliminar miembro":
        st.subheader("🗑️ Eliminar un miembro")

        miembros = obtener_miembros()
        lista = {f"{m[1]} (DUI {m[3]})": m[0] for m in miembros}

        seleccionado = st.selectbox("Seleccione un miembro:", list(lista.keys()))
        id_miembro = lista[seleccionado]

        if st.button("Eliminar definitivamente"):
            try:
                conexion = obtener_conexion()
                cursor = conexion.cursor()

                cursor.execute("DELETE FROM miembrogapc WHERE id_miembro=%s", (id_miembro,))
                conexion.commit()
                st.success("Miembro eliminado.")

            except Exception as e:
                st.error("Error al eliminar: " + str(e))

            finally:
                cursor.close()
                conexion.close()
