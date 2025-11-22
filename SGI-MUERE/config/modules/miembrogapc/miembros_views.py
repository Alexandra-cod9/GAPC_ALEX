import streamlit as st
from config.conexion import obtener_conexion

def form_agregar():
    st.subheader("Agregar miembro")

    nombre = st.text_input("Nombre completo")
    telefono = st.text_input("Teléfono")
    direccion = st.text_input("Dirección")

    if st.button("Guardar"):
        conexion = obtener_conexion()
        if conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO miembros (nombre, telefono, direccion)
                    VALUES (%s, %s, %s)
                """, (nombre, telefono, direccion))
                conexion.commit()
            st.success("Miembro agregado correctamente.")

def lista_miembros():
    st.subheader("Lista de miembros")

    conexion = obtener_conexion()
    if conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM miembros")
            datos = cursor.fetchall()

        st.table(datos)

def ver_miembro():
    st.subheader("Buscar miembro")

    nombre = st.text_input("Nombre")

    if st.button("Buscar"):
        conexion = obtener_conexion()
        if conexion:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT * FROM miembros WHERE nombre LIKE %s", (f"%{nombre}%",))
                result = cursor.fetchone()

            if result:
                st.json(result)
            else:
                st.warning("Miembro no encontrado.")
