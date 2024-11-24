# Contexto que regresa el usuario que inicio la sesion
def get_usuario(request):
    usuario = None
    # Verificamos si hay información del usuario en la sesión
    if 'usuario_id' in request.session:
        usuario = {
            'id': request.session.get('usuario_id'),
            'rol': request.session.get('usuario_rol'),
            'nombre': request.session.get('usuario_nombre'),
            'correo': request.session.get('usuario_correo'),
            'username': request.session.get('usuario_username'),
        }
    return {
        'usuario': usuario
    }