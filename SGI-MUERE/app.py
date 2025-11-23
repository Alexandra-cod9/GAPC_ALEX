import streamlit as st

# Utils
from utils.auth import login
from utils.navigation import menu

# Módulos
import modules.miembros as miembros
import modules.reuniones as reuniones
import modules.aportes as aportes
import modules.prestamos as prestamos
import modules.multas as multas
import modules.reportes as reportes
import modules.cierres as cierres
import modules.configuracion as configuracion


# =============================
#   CARGA DE CSS GLOBAL
# =============================
def load_css():
    try:
        with open("styles/theme.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        st.warning("No se pudo cargar el archivo CSS (styles/theme.css).")


# =============================
#        APLICACIÓN
# =============================
def main():
    # Cargar estilos primero para que afecten todo
    load_css()

    # Validación de sesión
    if "logged" not in st.session_state or not st.session_state["logged"]:
        login()
        return

    # Panel principal
    st.markdown(
        "<h1 style='color:#4b0082; font-weight:800;'>GAPT - Panel Principal</h1>",
        unsafe_allow_html=True
    )

    selected = menu()

    # =============================
    #   NAVEGACIÓN ENTRE MÓDULOS
    # =============================
    if selected == "Dashboard":
        st.header("Saldo Actual del Grupo")

        # Métrica principal
        st.metric("Saldo Total", "Q 12,500")

        st.write("Bienvenido al sistema GAPT. Usa el menú de la izquierda para navegar.")

    elif selected == "Miembros":
        miembros.show()

    elif selected == "Reuniones":
        reuniones.show()

    elif selected == "Aportes":
        aportes.show()

    elif selected == "Préstamos":
        prestamos.show()

    elif selected == "Multas":
        multas.show()

    elif selected == "Reportes":
        reportes.show()

    elif selected == "Cierres":
        cierres.show()

    elif selected == "Configuración":
        configuracion.show()


# Ejecución principal
if __name__ == "__main__":
    main()
