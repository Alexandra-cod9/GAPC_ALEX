import streamlit as st

def show():
    st.markdown(
        "<h1 style='color:#4b0082; font-weight:800;'>Gestión de Miembros</h1>",
        unsafe_allow_html=True
    )

    # Selección de acción
    opcion = st.radio(
        "Opciones",
        ["Ver miembros", "Agregar miembro"]
    )

    # =============================
    #       VER MIEMBROS
    # =============================
    if opcion == "Ver miembros":
        st.subheader("Lista de miembros del grupo")

        # Tabla de ejemplo (luego conectarás a MySQL)
        data = {
            "Nombre": ["Juan Pérez", "Ana López"],
            "DPI": ["123456789", "987654321"],
            "Teléfono": ["5555-1234", "5555-7667"]
        }

        st.table(data)

    # =============================
    #       AGREGAR MIEMBRO
    # =============================
    elif opcion == "Agregar miembro":
        st.subheader("Nuevo miembro")

        nombre = st.text_input("Nombre completo")
        dpi = st.text_input("DPI")
        tel = st.text_input("Teléfono")

        if st.button("Guardar"):
            # Aquí después pondrás INSERT INTO MySQL
            st.success("Miembro agregado exitosamente.")
