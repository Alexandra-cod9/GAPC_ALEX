# utils/helpers.py
import streamlit as st
from datetime import datetime

def formatear_fecha(fecha):
    """Formatea fecha para mostrar"""
    if fecha:
        return fecha.strftime("%d/%m/%Y")
    return ""

def formatear_moneda(monto):
    """Formatea monto como moneda"""
    if monto:
        return f"${monto:,.2f}"
    return "$0.00"

def validar_campos_obligatorios(campos):
    """Valida que los campos obligatorios no estén vacíos"""
    for campo, valor in campos.items():
        if not valor:
            st.error(f"El campo '{campo}' es obligatorio")
            return False
    return True
