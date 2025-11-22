# Consultas para el módulo de autenticación
QUERIES_AUTH = {
    'login': """
        SELECT id_miembro, nombre, correo, contrasena, id_rol 
        FROM miembrogapc 
        WHERE correo = %s AND contrasena IS NOT NULL 
    """,
    'obtener_usuario': """
        SELECT m.id_miembro, m.nombre, m.correo, r.tipo_rol
        FROM miembrogapc m
        JOIN rol r ON m.id_rol = r.id_rol
        WHERE m.id_miembro = %s
    """
}

# Consultas para dashboard
QUERIES_DASHBOARD = {
    'estadisticas_grupo': """
        SELECT COUNT(*) as total_miembros 
        FROM miembrogapc 
        WHERE id_grupo = %s
    """,
    'reuniones_recientes': """
        SELECT fecha, acuerdos 
        FROM reunion 
        WHERE id_grupo = %s 
        ORDER BY fecha DESC 
        LIMIT 5
    """
}
