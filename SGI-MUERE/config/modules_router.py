import streamlit as st

def cargar_modulo(nombre):
    if nombre == "Miembros":
        from config.modules.miembrogapc import menu_miembros
        menu_miembros.cargar()

    elif nombre == "Aportes":
        from config.modules.aportes import menu_aportes
        menu_aportes.cargar()

    elif nombre == "Reuniones":
        from config.modules.reunion import menu_reuniones
        menu_reuniones.cargar()

    elif nombre == "Préstamos":
        from config.modules.prestamo import menu_prestamos
        menu_prestamos.cargar()

    elif nombre == "Multas":
        from config.modules.multa import menu_multas
        menu_multas.cargar()

    elif nombre == "Cierre":
        from config.modules.cierre import menu_cierre
        menu_cierre.cargar()

    elif nombre == "Reportes":
        from config.modules.dashboard import menu_reportes
        menu_reportes.cargar()

    elif nombre == "Configuraciones":
        from config.modules.grupo import menu_configuraciones
        menu_configuraciones.cargar()

    else:
        st.info("Módulo no encontrado")
