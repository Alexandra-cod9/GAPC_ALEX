from config.conexion import obtener_conexion

def verificar_login_real(correo, contrasena):
    """Verifica credenciales contra la base de datos"""
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            cursor.execute("""
                SELECT m.id_miembro, m.nombre, m.correo, m.contrasena, r.tipo_rol, m.id_grupo
                FROM miembrogapc m
                JOIN rol r ON m.id_rol = r.id_rol
                WHERE m.correo = %s AND m.contrasena IS NOT NULL
            """, (correo,))
            
            usuario = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if usuario and usuario['contrasena'] == contrasena:
                return {
                    'id': usuario['id_miembro'],
                    'nombre': usuario['nombre'],
                    'correo': usuario['correo'],
                    'tipo_rol': usuario['tipo_rol'],
                    'id_grupo': usuario['id_grupo']
                }
        return None
    except Exception as e:
        print(f"Error al verificar login: {e}")
        return None
