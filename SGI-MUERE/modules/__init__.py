# Exportar todas las funciones de los módulos
from .dashboard import mostrar_dashboard_principal
from .miembros import mostrar_modulo_miembros
from .reuniones import mostrar_modulo_reuniones
from .aportes import mostrar_modulo_aportes
from .prestamos import mostrar_modulo_prestamos
from .multas import mostrar_modulo_multas
from .reportes import mostrar_modulo_reportes
from .cierre import mostrar_modulo_cierre
from .info_grupo import mostrar_modulo_info_grupo  # Cambiado de configuracion a info_grupo

__all__ = [
    'mostrar_dashboard_principal',
    'mostrar_modulo_miembros',
    'mostrar_modulo_reuniones',
    'mostrar_modulo_aportes',
    'mostrar_modulo_prestamos',
    'mostrar_modulo_multas',
    'mostrar_modulo_reportes',
    'mostrar_modulo_cierre',
    'mostrar_modulo_info_grupo'  # Cambiado aquí también
]
