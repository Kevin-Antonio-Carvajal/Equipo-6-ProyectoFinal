
from django.db.models import Q, Max
from django.contrib import messages
from django.http import JsonResponse
from .forms import FormRegistro, FormLogin
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from mainapp.context_processors import get_usuario
from mainapp.CryptoUtils import cipher, sha256, validate
from .models import Usuario, Rol, Comic, Mensaje, ListaDeseos


def index(request):

     # Obtener los 6 cómics más recientes que no han sido vendidos
    comics_recientes = Comic.objects.filter(venta__isnull=True).order_by('-created_at')[:6]

    contexto = {
        'titulo': 'Pagina principal',
        'comics': comics_recientes
    }

    return render(request, 'mainapp/index.html', contexto)

def register(request):
    contexto = {
        'titulo': 'Registrarse',
        'form': FormRegistro()
    }   
    if request.method == 'POST':
        formulario = FormRegistro(request.POST)
        if formulario.is_valid():
            data_form = formulario.cleaned_data            
            nombre = data_form.get('nombre')
            correo = data_form.get('correo')
            username = data_form.get('username')            
            password = data_form.get('password')
            rol_id = data_form.get('rol')
            # Verificar si el correo ya está registrado
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'Este correo electrónico ya está registrado. Si ya tienes una cuenta, por favor inicia sesión.')
                contexto['form'] = formulario
                return render(request, 'mainapp/register.html', contexto)
            # Verificar si el nombre de usuario ya está registrado
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'Este nombre de usuario ya está registrado. Elige otro nombre de usuario')
                contexto['form'] = formulario
                return render(request, 'mainapp/register.html', contexto)
            try:
                # Obtener el objeto Rol a partir del ID
                rol = Rol.objects.get(id_rol=rol_id)
            except Rol.DoesNotExist:
                messages.error(request, 'El rol seleccionado no es válido.')
                contexto['form'] = formulario
                return render(request, 'mainapp/register.html', contexto)
            # Registrar nuevo usuario con contraseña cifrada
            hashed_password = sha256(cipher(password)).hexdigest()
            Usuario.objects.create(
                rol=rol,
                nombre=nombre,                
                correo=correo,
                username=username,                
                password=hashed_password
            )
            messages.success(request, 'Te has registrado correctamente')
            return redirect('inicio')
        else:
            # Si el formulario no es válido, mostramos los errores
            for field, errors in formulario.errors.items():
                for error in errors:
                    messages.error(request, error)                
            # En caso de error, volvemos a pasar el formulario con los datos ingresados
            contexto['form'] = formulario
            return render(request, 'mainapp/register.html', contexto)
    # Renderizamos la vista con el formulario inicial (GET)
    else:         
        return render(request, 'mainapp/register.html', contexto)   

def login(request):
    contexto = {
        'titulo': 'Iniciar Sesión',
        'form': FormLogin()
    }
    if request.method == 'POST':
        formulario = FormLogin(request.POST)
        if formulario.is_valid():
            data_form = formulario.cleaned_data
            correo = data_form.get('correo')
            password = data_form.get('password')
            # Verificamos que exista el correo ya esta registrado
            if not Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'Correo electrónico incorrecto')
                contexto['form'] = formulario
                return render(request, 'mainapp/login.html', contexto)
            # Obtenemos al usuario por el correo
            usuario = Usuario.objects.get(correo=correo)
            if validate(password,usuario.password):
                # Guardamos la informacion del usuario en la sesion
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_rol'] = usuario.rol.id_rol
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_correo'] = usuario.correo
                request.session['usuario_username'] = usuario.username
                messages.success(request, f'Bienvenido, {usuario.nombre}!')
                return redirect('index')
            else:
                messages.error(request, 'Contraseña incorrecta')
                contexto['form'] = formulario
                return render(request, 'mainapp/login.html', contexto)
    else:
        return render(request, 'mainapp/login.html', contexto)    

def logout(request):
    # Limpiamos toda la información almacenada en la sesión
    request.session.flush()
    # Mostramos un mensaje de éxito al cerrar sesión
    messages.success(request, 'Has cerrado sesión exitosamente')
    # Redirigimos al usuario a la página de inicio de sesión
    return redirect('login')

def registrar_comic(request):
    # Obtenemos el usuario que inicio sesion
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')
    # Verificamos que se haya iniciado sesion
    if usuario is None:
        messages.error(request, 'Debes iniciar sesión para registrar un producto')
        return redirect('login')
    # Verificamos que el usuario sea vendedor
    if usuario['rol'] != 3:
        messages.error(request, 'Solo los vendedores pueden registrar un producto')
        return redirect('index')
    contexto = {
        'titulo': 'Registrar Nuevo Cómic'
    }
    return render(request, 'mainapp/registrar_comic.html', contexto)

def crear_comic(request):    
    if request.method == 'POST':
        # Obtenemos el usuario que inicio sesion
        usuario_contexto = get_usuario(request)
        usuario = usuario_contexto.get('usuario')
        # Verificamos que se haya iniciado sesion
        if usuario is None:
            error = 'Debes iniciar sesion para registrar un producto'
            messages.error(request, error)
            return JsonResponse({'success': False, 'error': error}, status=403)
        # Verificamos el rol del usuario
        if usuario['rol'] != 3:
            error = 'Solo los vendedores pueden registrar un producto'
            messages.error(request, error)
            return JsonResponse({'success': False, 'error': error}, status=403)
        # Obtenemos los datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')
        # Validamos la información
        if not nombre or not imagen:
            error = 'El nombre y la imagen son obligatorios'
            messages.error(request, error)
            return JsonResponse({'success': False, 'error': error}, status=400)
        # Obtenemos el vendedor
        vendedor = None
        try:
            vendedor = Usuario.objects.get(id_usuario=usuario['id'])
        except Usuario.DoesNotExist:
            error = 'El vendedor no existe'
            messages.error(request, error)
            return JsonResponse({'success': False, 'error': error}, status=404)
        # Creamos el producto
        comic = Comic.objects.create(
            vendedor=vendedor,
            nombre=nombre,
            descripcion=descripcion,
            imagen=imagen
        )
        success = 'Comic registrado exitosamente'
        messages.success(request, success)
        return JsonResponse({'success': True, 'message': success}, status=200)
    return JsonResponse({'success': False, 'error': 'Metodo invalido'}, status=400)

def buscar_comics(request):
    query = request.GET.get('q', '')
    titulo = 'Búsqueda de cómics'

    if query:
        # Filtrar los cómics según el término de búsqueda
        comics = Comic.objects.select_related('vendedor').filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query),
            venta__isnull=True  # Asegurarse de incluir solo cómics no vendidos
        )
        titulo = f"Resultados de búsqueda para '{query}'"
    else:
        # Obtener todos los cómics no vendidos
        comics = Comic.objects.select_related('vendedor').filter(venta__isnull=True)

    # Si no se encontraron cómics
    if not comics.exists():  # Usar .exists() para verificar si hay resultados
        titulo = "No se han encontrado cómics"

    contexto = {
        'titulo': titulo,
        'comics': comics,
        'busqueda': query
    }
    return render(request, 'mainapp/buscar_comics.html', contexto)

def detalle_comic(request, comic_id):
    comic = get_object_or_404(Comic, id_comic=comic_id)
    contexto = {
        'titulo': comic.nombre,
        'comic': comic
    }
    return render(request, 'mainapp/detalle_comic.html', contexto)

def ver_lista_deseos(request):
    # Obtenemos el usuario que inicio sesion
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')
    # Verificamos que se haya iniciado sesion
    if usuario is None:
        messages.error(request, 'Debes iniciar sesión para registrar un producto')
        return redirect('login')
    # Verificamos que el usuario sea un comprador
    if usuario['rol'] != 2:
        messages.error(request, 'Solo los compradores pueden ver su lista de deseos')
        return redirect('index')

    lista_deseos = ListaDeseos.objects.filter(usuario__id_usuario=usuario['id'])
    contexto = {
        'titulo': 'Mi Lista de Deseos',
        'lista_deseos': lista_deseos,
    }
    return render(request, 'mainapp/lista_deseos.html', contexto)

def agregar_a_lista_deseos(request, comic_id):
    if request.method == "POST":
        # Obtenemos el usuario que inicio sesion
        usuario_contexto = get_usuario(request)
        usuario = usuario_contexto.get('usuario')
        # Verificamos que se haya iniciado sesion
        if usuario is None:
            messages.error(request, 'Debes iniciar sesión para agregar a la lista de deseos')
            return redirect('login')
        # Verificamos que el usuario sea un comprador
        if usuario['rol'] != 2:
            messages.error(request, 'Solo los compradores pueden agregar a su lista de deseos')
            return redirect('index')

        # Obtener el cómic
        comic = get_object_or_404(Comic, id_comic=comic_id)
        
        # Obtener al usuario logueado
        usuario = Usuario.objects.get(id_usuario=usuario['id'])
        
        # Verificar si ya está en la lista de deseos
        if ListaDeseos.objects.filter(usuario=usuario, comic=comic).exists():
            messages.warning(request, "El cómic ya está en tu lista de deseos.")
        else:
            # Agregar el cómic a la lista de deseos
            ListaDeseos.objects.create(usuario=usuario, comic=comic)
            messages.success(request, "El cómic se agregó a tu lista de deseos.")
        
        return redirect('ver_lista_deseos')
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def eliminar_de_lista_deseos(request, comic_id):
    # Obtenemos el usuario que inicio sesion
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')

    if usuario is None:
        return JsonResponse({'success': False, 'error': 'Debes iniciar sesión para modificar la lista de deseos'}, status=403)
    
    # Verificamos que el usuario sea un comprador
    if usuario['rol'] != 2:
        messages.error(request, 'Solo los compradores pueden eliminar de su lista de deseos')
        return redirect('index')

    try:
        # Intentar eliminar el cómic de la lista de deseos
        ListaDeseos.objects.filter(usuario_id=usuario['id'], comic_id=comic_id).delete()
        # messages.success(request, 'Cómic eliminado de tu lista de deseos')
        return JsonResponse({'success': True, 'message': 'Cómic eliminado de tu lista de deseos'}, status=200)
    except Exception as e:
        # Log para depuración
        print(f"Error al eliminar el cómic: {e}")
        # messages.error(request, 'Error al eliminar el comic')
        return JsonResponse({'success': False, 'error': 'Error al eliminar el comic.'}, status=500)
    
def mensajes(request):
    # Obtenemos el usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')
    
    # Verificamos que se haya iniciado sesión
    if usuario is None:
        messages.error(request, 'Debes iniciar sesión para poder ver tus mensajes')
        return redirect('login')
    
    # Obtenemos el ID del usuario actual
    usuario_id = usuario.get('id')
    
    # Obtener los últimos mensajes por chat con cada usuario
    mensajes_usuario = Mensaje.objects.filter(
        Q(emisor_id=usuario_id) | Q(receptor_id=usuario_id)
    ).annotate(ultima_fecha=Max('fecha_emision')).values(
        'emisor_id', 'receptor_id', 'ultima_fecha'
    )

    # Usamos un diccionario para evitar repetidos
    chats_unicos = {}

    for mensaje in mensajes_usuario:
        # Determinamos el otro usuario en la conversación
        otro_usuario_id = mensaje['emisor_id'] if mensaje['emisor_id'] != usuario_id else mensaje['receptor_id']
        
        # Evitar duplicados en el diccionario
        if otro_usuario_id not in chats_unicos:
            # Obtener el último mensaje entre ambos usuarios
            ultimo_mensaje = Mensaje.objects.filter(
                Q(emisor_id=usuario_id, receptor_id=otro_usuario_id) | 
                Q(receptor_id=usuario_id, emisor_id=otro_usuario_id),
                fecha_emision=mensaje['ultima_fecha']
            ).first()
            
            # Obtener los datos del otro usuario
            otro_usuario = Usuario.objects.filter(id_usuario=otro_usuario_id).values(
                'id_usuario', 'username', 'nombre', 'correo'
            ).first()

            # Agregar datos al diccionario de chats únicos
            if otro_usuario and ultimo_mensaje:
                chats_unicos[otro_usuario_id] = {
                    'usuario': otro_usuario,
                    'ultimo_mensaje': ultimo_mensaje
                }

    # Convertir los valores del diccionario en una lista para el contexto
    chats = list(chats_unicos.values())

    # Contexto para la plantilla
    contexto = {
        'titulo': 'Chats',
        'chats': chats
    }
    
    return render(request, 'mainapp/mensajes.html', contexto)

def get_mensajes(request, id_usuario):
    # Obtenemos el usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')
    # Verificamos que haya iniciado sesión
    if usuario is None:
        return JsonResponse(
            {'success': False, 'error': 'Debes iniciar sesión para obtener los mensajes con un usuario'}, 
            status=403
        )
    # Verificamos que el id_usuario sea válido
    if not id_usuario:
        return JsonResponse(
            {'success': False, 'error': 'El ID del usuario destinatario no es válido'}, 
            status=400
        )
    # Serializamos la información del usuario que inició sesión
    usuario_actual_serializado = {
        'id': usuario.get('id'),
        'nombre': usuario.get('nombre'),
        'correo': usuario.get('correo'),
        'username': usuario.get('username')
    }
    # Obtenemos los datos del usuario relacionado
    try:
        usuario_chat = Usuario.objects.get(id_usuario=id_usuario)
        usuario_chat_serializado = {
            'id': usuario_chat.id_usuario,
            'nombre': usuario_chat.nombre,
            'correo': usuario_chat.correo,
            'username': usuario_chat.username
        }
    except Usuario.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'El usuario destinatario no existe'}, 
            status=404
        )
    # Obtenemos los mensajes entre el usuario actual y el usuario con id_usuario
    usuario_actual_id = usuario.get('id')  # ID del usuario actual de la sesión
    mensajes = Mensaje.objects.filter(
        Q(emisor_id=usuario_actual_id, receptor_id=id_usuario) | 
        Q(emisor_id=id_usuario, receptor_id=usuario_actual_id)
    ).order_by('fecha_emision')
    # Serializamos los mensajes
    mensajes_serializados = [
        {
            'id': mensaje.id_mensaje,
            'contenido': mensaje.contenido,
            'emisor_id': mensaje.emisor_id,
            'receptor_id': mensaje.receptor_id,
            'fecha_emision': mensaje.fecha_emision.strftime('%Y-%m-%d %H:%M:%S'),
            'visto': mensaje.visto
        }
        for mensaje in mensajes
    ]
    return JsonResponse(
        {
            'success': True,
            'message': 'Mensajes recuperados',
            'usuario_actual': usuario_actual_serializado,
            'usuario_chat': usuario_chat_serializado,
            'mensajes': mensajes_serializados
        },
        status=200
    )

def mandar_mensaje(request):
    if request.method == 'POST':
        # Obtenemos el usuario que inicio sesion
        usuario_contexto = get_usuario(request)
        usuario = usuario_contexto.get('usuario')
        # Verificamos que se haya iniciado sesion
        if usuario is None:
            error = 'Debes iniciar sesion para mandar un mensaje'
            return JsonResponse({'success': False, 'error': error}, status=403)
        # Obtenemos los datos del formulario
        id_emisor = request.POST.get('idUsuarioEmisor')
        id_receptor = request.POST.get('idUsuarioReceptor')
        contenido = request.POST.get('mensaje') # Contenido del mensaje
        # Validaciones
        if not id_emisor or not id_receptor or not contenido:
            error = 'Faltan datos obligatorios para registrar el mensaje'
            return JsonResponse({'success': False, 'error': error}, status=400)
        # Verificamos que el id del emisor sea el mismo que el inicio sesion
        if (usuario['id'] != int(id_emisor)):
            error = 'El ID del usuario que inició sesión es distinto al ID del emisor'
            return JsonResponse({'success': False, 'error': error}, status=403)
        # Registramos el mensaje
        try:
            # Verificamos que el receptor exista
            receptor = Usuario.objects.get(id_usuario=id_receptor)
            # Registramos el mensaje
            Mensaje.objects.create(
                emisor_id=id_emisor,
                receptor=receptor,
                contenido=contenido
            )
            # Respuesta exitosa
            success = 'Mensaje enviado exitosamente'
            return JsonResponse({'success': True, 'message': success}, status=200)
        except Usuario.DoesNotExist:
            error = 'El usuario receptor no existe'
            return JsonResponse({'success': False, 'error': error}, status=404)
        except Exception as e:
            error = f'Error al registrar el mensaje: {str(e)}'
            return JsonResponse({'success': False, 'error': error}, status=500)
    return JsonResponse({'success': False, 'error': 'Metodo invalido'}, status=400)