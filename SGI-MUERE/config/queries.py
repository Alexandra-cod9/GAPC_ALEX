# config/queries.py

# Queries para Miembros
QUERY_OBTENER_MIEMBROS = """
    SELECT * FROM miembros 
    WHERE estado = 'activo' 
    ORDER BY nombre
"""

QUERY_BUSCAR_MIEMBRO = """
    SELECT * FROM miembros 
    WHERE nombre LIKE %s OR cedula LIKE %s 
    ORDER BY nombre 
    LIMIT 10
"""

QUERY_INSERTAR_MIEMBRO = """
    INSERT INTO miembros (nombre, cedula, telefono, email, direccion, fecha_ingreso, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

QUERY_OBTENER_MIEMBRO_POR_ID = """
    SELECT * FROM miembros WHERE id = %s
"""

# Queries para Aportes
QUERY_OBTENER_APORTES_MIEMBRO = """
    SELECT * FROM aportes 
    WHERE miembro_id = %s 
    ORDER BY fecha_aporte DESC 
    LIMIT 20
"""

QUERY_INSERTAR_APORTE = """
    INSERT INTO aportes (miembro_id, tipo_aporte, monto, fecha_aporte, descripcion)
    VALUES (%s, %s, %s, %s, %s)
"""

QUERY_OBTENER_TOTAL_APORTES_MES = """
    SELECT COALESCE(SUM(monto), 0) as total 
    FROM aportes 
    WHERE MONTH(fecha_aporte) = MONTH(CURRENT_DATE())
"""

# Queries para Préstamos
QUERY_OBTENER_PRESTAMOS_MIEMBRO = """
    SELECT * FROM prestamos 
    WHERE miembro_id = %s 
    ORDER BY fecha_prestamo DESC
"""

QUERY_OBTENER_PRESTAMOS_ACTIVOS = """
    SELECT COUNT(*) as total FROM prestamos WHERE estado = 'activo'
"""

# Queries para Multas
QUERY_OBTENER_MULTAS_MIEMBRO = """
    SELECT * FROM multas 
    WHERE miembro_id = %s 
    ORDER BY fecha_multa DESC
"""

QUERY_OBTENER_MULTAS_PENDIENTES = """
    SELECT COUNT(*) as total FROM multas WHERE estado = 'pendiente'
"""

# Query para historial completo
QUERY_OBTENER_HISTORIAL_MIEMBRO = """
    SELECT 'Aporte' as tipo, fecha_aporte as fecha, monto 
    FROM aportes WHERE miembro_id = %s
    UNION ALL
    SELECT 'Préstamo' as tipo, fecha_prestamo as fecha, monto 
    FROM prestamos WHERE miembro_id = %s
    UNION ALL  
    SELECT 'Multa' as tipo, fecha_multa as fecha, monto 
    FROM multas WHERE miembro_id = %s
    ORDER BY fecha DESC 
    LIMIT 30
"""
