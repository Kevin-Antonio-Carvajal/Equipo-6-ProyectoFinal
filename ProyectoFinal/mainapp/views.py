
from django.db import transaction
from django.db.models import Q, Max, Exists, OuterRef, Subquery
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from .forms import FormRegistro, FormLogin
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from mainapp.context_processors import get_usuario
from mainapp.CryptoUtils import cipher, sha256, validate
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

def index(request):
    # Usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')

    # Inicializar la cantidad de mensajes sin leer
    mensajes = 0

    if usuario is not None:
        # Obtener la cantidad de mensajes sin leer del usuario
        mensajes = Mensaje.objects.filter(receptor_id=usuario['id'], visto=False).count()

    # Obtener los 6 cómics más recientes que no han sido vendidos
    comics_recientes = Comic.objects.filter(venta__isnull=True).order_by('-created_at')[:6]

    # Construir el contexto para el template
    contexto = {
        'titulo': 'Pagina principal',
        'comics': comics_recientes,
        'mensajes': mensajes
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
        # Obtenemos el usuario que inició sesión
        usuario_contexto = get_usuario(request)
        usuario = usuario_contexto.get('usuario')
        # Verificamos que se haya iniciado sesión
        if usuario is None:
            error = 'Debes iniciar sesión para registrar un producto'
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
        # Creamos el cómic
        comic = Comic.objects.create(
            vendedor=vendedor,
            nombre=nombre,
            descripcion=descripcion,
            imagen=imagen
        )
        
        # Enviar notificación a todos los administradores
        administradores = Usuario.objects.filter(
            rol=1  # Rol de administrador
        )
        for admin in administradores:
            Notificacion.objects.create(
                usuario=admin,
                contenido=f"Se ha registrado un nuevo cómic: '{comic.nombre}' por el vendedor {vendedor.username}."
            )

        # Respuesta de éxito
        success = 'Comic registrado exitosamente y notificaciones enviadas a los administradores'
        messages.success(request, success)
        return JsonResponse({'success': True, 'message': success}, status=200)

    return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)

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
    # Obtenemos el usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')

    # Verificamos que se haya iniciado sesión
    if usuario is None:
        messages.error(request, 'Debes iniciar sesión para ver tu lista de deseos')
        return redirect('login')

    # Verificamos que el usuario sea un comprador
    if usuario['rol'] != 2:
        messages.error(request, 'Solo los compradores pueden ver su lista de deseos')
        return redirect('index')

    # Subconsulta para obtener la oferta más reciente relacionada con el cómic
    oferta_reciente = Oferta.objects.filter(
        comic_id=OuterRef('comic_id')
    ).order_by('-fecha_emision')  # Ordenamos por fecha de emisión más reciente

    # Consulta con anotación para incluir la oferta relacionada y su estado
    lista_deseos = ListaDeseos.objects.filter(usuario__id_usuario=usuario['id']).annotate(
        oferta_relacionada=Exists(oferta_reciente),
        oferta_id=Subquery(oferta_reciente.values('id_oferta')[:1]),
        oferta_estado=Subquery(oferta_reciente.values('aceptada')[:1])
    )

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

        # Verificar si ya está en la lista de deseos
        comprador = Usuario.objects.get(id_usuario=usuario['id'])
        if ListaDeseos.objects.filter(usuario=comprador, comic=comic).exists():
            messages.warning(request, "El cómic ya está en tu lista de deseos.")
        else:
            # Agregar el cómic a la lista de deseos
            ListaDeseos.objects.create(usuario=comprador, comic=comic)
            messages.success(request, "El cómic se agregó a tu lista de deseos.")

        # Obtener la URL de referencia
        referer_url = request.META.get('HTTP_REFERER', None)
        
        # Redirigir a la página de referencia o a una página por defecto
        if referer_url:
            return HttpResponseRedirect(referer_url)
        return redirect('index')  # Redirige al inicio si no hay una URL de referencia

    messages.error(request, 'Método no permitido.')
    return redirect('index')

def eliminar_de_lista_deseos(request, comic_id):
    # Obtenemos el usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')

    if usuario is None:
        return JsonResponse({'success': False, 'error': 'Debes iniciar sesión para modificar la lista de deseos'}, status=403)
    
    # Verificamos que el usuario sea un comprador
    if usuario['rol'] != 2:
        messages.error(request, 'Solo los compradores pueden eliminar de su lista de deseos')
        return redirect('index')

    try:
        with transaction.atomic():  # Garantiza que las operaciones sean atómicas
            # Obtener el cómic
            comic = get_object_or_404(Comic, id_comic=comic_id)

            # Eliminar todas las ofertas relacionadas al cómic
            ofertas = Oferta.objects.filter(comic_id=comic_id)
            for oferta in ofertas:
                # Enviar mensaje al receptor notificando la eliminación de cada oferta
                mensaje_contenido = f"El usuario '{usuario['username']}' eliminó la oferta '{oferta.objeto}' por el cómic '{comic.nombre}'"
                Mensaje.objects.create(
                    emisor=Usuario.objects.get(id_usuario=usuario['id']),
                    receptor=comic.vendedor,
                    contenido=mensaje_contenido
                )
            # Eliminar las ofertas
            ofertas.delete()

            # Eliminar el cómic de la lista de deseos
            ListaDeseos.objects.filter(usuario_id=usuario['id'], comic_id=comic_id).delete()

        # Enviar una respuesta exitosa
        return JsonResponse({'success': True, 'message': 'Cómic eliminado de tu lista de deseos y todas las ofertas relacionadas eliminadas'}, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

    except Exception as e:
        # Log para depuración
        print(f"Error al eliminar el cómic o la oferta: {e}")
        return JsonResponse({'success': False, 'error': 'Error al eliminar el cómic o la oferta relacionada.'}, status=500)
    
def hacer_oferta(request, comic_id):
    if request.method == "POST":
        # Obtenemos el usuario que inició sesión
        usuario_contexto = get_usuario(request)
        usuario = usuario_contexto.get('usuario')
        if usuario is None:
            return JsonResponse({'success': False, 'error': 'Debes iniciar sesión para hacer una oferta'}, status=403)

        # Obtener el cómic al que se quiere hacer una oferta
        comic = get_object_or_404(Comic, id_comic=comic_id)

        # Obtener los datos del formulario
        objeto = request.POST.get('objeto')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')

        # Crear la oferta
        oferta = Oferta.objects.create(
            comic=comic,
            emisor=Usuario.objects.get(id_usuario=usuario['id']),
            receptor=comic.vendedor,
            objeto=objeto,
            descripcion=descripcion,
            imagen=imagen
        )

        # Agregar el cómic a la lista de deseos si no está ya incluido
        comprador = Usuario.objects.get(id_usuario=usuario['id'])
        if not ListaDeseos.objects.filter(usuario=comprador, comic=comic).exists():
            ListaDeseos.objects.create(usuario=comprador, comic=comic)

        # Enviar mensaje al vendedor
        mensaje_contenido = f"Te hice una oferta por el comic '{comic.nombre}' a cambio del objeto '{objeto}'"
        Mensaje.objects.create(
            emisor=comprador,
            receptor=comic.vendedor,
            contenido=mensaje_contenido
        )

        # Obtener la URL de referencia
        referer_url = request.META.get('HTTP_REFERER', None)
        messages.success(request, 'Oferta realizada exitosamente y el cómic se ha añadido a tu lista de deseos.')

        # Redirigir a la página de referencia o a una página por defecto
        if referer_url:
            return HttpResponseRedirect(referer_url)
        return redirect('index') 

    messages.error(request, 'Método no permitido.')
    return redirect('index')

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

    # Obtener los últimos mensajes únicos por usuario con anotación
    mensajes_usuario = Mensaje.objects.filter(
        Q(emisor_id=usuario_id) | Q(receptor_id=usuario_id)
    ).annotate(
        ultima_fecha=Max('fecha_emision')
    ).values(
        'emisor_id', 'receptor_id', 'ultima_fecha'
    )

    # Usamos un diccionario para evitar duplicados por conversación
    chats_unicos = {}

    for mensaje in mensajes_usuario:
        # Determinamos el otro usuario en la conversación
        otro_usuario_id = mensaje['emisor_id'] if mensaje['emisor_id'] != usuario_id else mensaje['receptor_id']

        # Evitar duplicados
        if otro_usuario_id not in chats_unicos:
            # Obtener el último mensaje entre ambos usuarios
            ultimo_mensaje = Mensaje.objects.filter(
                Q(emisor_id=usuario_id, receptor_id=otro_usuario_id) |
                Q(receptor_id=usuario_id, emisor_id=otro_usuario_id)
            ).order_by('-fecha_emision').first()

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

    # Verificar si hay mensajes sin leer
    hay_mensajes_sin_leer = Mensaje.objects.filter(
        receptor_id=usuario_id,
        visto=False
    ).exists()

    # Convertir los valores del diccionario en una lista para el contexto
    chats = list(chats_unicos.values())

    # Contexto para la plantilla
    contexto = {
        'titulo': 'Chats',
        'chats': chats,
        'hay_mensajes_sin_leer': hay_mensajes_sin_leer  # Bandera para mensajes no leídos
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
    
    # Marcar como vistos todos los mensajes recibidos por el usuario actual de este chat
    Mensaje.objects.filter(
        receptor_id=usuario_actual_id,
        emisor_id=id_usuario,
        visto=False
    ).update(visto=True)

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

def obtener_notificaciones(request):
    # Verificamos si el usuario ha iniciado sesión mediante la sesión
    usuario_id = request.session.get('usuario_id')
    usuario_rol = request.session.get('usuario_rol')

    if not usuario_id:  
        return JsonResponse({'error': 'No autorizado'}, status=403)

    data = []

    # Para vendedores
    if usuario_rol == 3:  # Rol vendedor
        receptor = get_object_or_404(Usuario, id_usuario=usuario_id)
        ofertas_no_vistas = Oferta.objects.filter(receptor=receptor, visto=False).select_related('comic', 'emisor')
        data.extend([
            {
                'id': oferta.id_oferta,
                'tipo': 'oferta',
                'mensaje': f"Has recibido una nueva oferta por '{oferta.comic.nombre}' de {oferta.emisor.username}.",
                'objeto': oferta.objeto,
                'comic': oferta.comic.nombre,
                'emisor': oferta.emisor.username,
            }
            for oferta in ofertas_no_vistas
        ])

    # Para compradores
    if usuario_rol == 2:  # Rol comprador
        emisor = get_object_or_404(Usuario, id_usuario=usuario_id)
        notificaciones = Notificacion.objects.filter(usuario=emisor, visto=False)
        data.extend([
            {
                'id': notificacion.id_notificacion,
                'tipo': 'notificacion',
                'mensaje': notificacion.contenido,
                'fecha': notificacion.fecha_emision.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for notificacion in notificaciones
        ])

    return JsonResponse({'notificaciones': data})


@csrf_exempt
def marcar_notificacion_vista(request, oferta_id):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        if usuario_id:
            receptor = get_object_or_404(Usuario, id_usuario=usuario_id)  
            oferta = get_object_or_404(Oferta, id_oferta=oferta_id, receptor=receptor)
            oferta.visto = True
            oferta.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'No autorizado'}, status=403)


def ofertas(request):
    # Obtenemos el usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')

    if usuario is None:
        messages.error(request, 'Debes iniciar sesión para poder ver las ofertas que te han hecho')
        return redirect('login')
    
    # Obtener el ID del usuario desde el diccionario
    usuario_id = usuario.get('id')
    
    # Filtrar las ofertas donde el usuario es el receptor
    ofertas_recibidas = Oferta.objects.filter(receptor_id=usuario_id).select_related('comic', 'emisor')

    contexto = {
        'titulo': 'Ofertas',
        'ofertas': ofertas_recibidas
    }

    return render(request, 'mainapp/ofertas.html', contexto)

def aceptar_oferta(request, id_oferta):
    # Obtenemos el usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')

    # Verificamos que se haya iniciado sesión
    if usuario is None:
        return JsonResponse({'success': False, 'error': 'Se necesita iniciar sesión para aceptar una oferta'}, status=403)

    # Verificamos que el rol del usuario sea de un vendedor
    if usuario['rol'] != 3:  # Asumimos que el rol 3 corresponde a vendedores
        return JsonResponse({'success': False, 'error': 'Solo los usuarios con rol de vendedor pueden aceptar ofertas'}, status=403)

    # Obtenemos la oferta
    oferta = get_object_or_404(Oferta, id_oferta=id_oferta)

    # Verificamos que el usuario actual sea el receptor de la oferta
    if oferta.receptor.id_usuario != usuario['id']:
        return JsonResponse({'success': False, 'error': 'No puedes aceptar una oferta que no te pertenece'}, status=403)

    # Aceptamos la oferta
    oferta.aceptada = True
    oferta.visto = True
    oferta.save()

    # Marcamos otras ofertas del mismo cómic como rechazadas
    Oferta.objects.filter(comic=oferta.comic, aceptada__isnull=True).exclude(id_oferta=id_oferta).update(aceptada=False, visto=True)

    # Creamos un registro de venta
    Venta.objects.create(
        comic=oferta.comic,
        comprador=oferta.emisor,
        oferta=oferta
    )

    # Enviamos un mensaje al comprador
    Mensaje.objects.create(
        emisor_id=oferta.receptor.id_usuario,  # El vendedor que acepta
        receptor_id=oferta.emisor.id_usuario,  # El comprador al que se notifica
        contenido=f"Tu oferta por el cómic '{oferta.comic.nombre}' ha sido aceptada."
    )

    # Creamos una notificación para el comprador
    Notificacion.objects.create(
        usuario_id=oferta.emisor.id_usuario,  # El comprador que debe ser notificado
        contenido=f"¡Felicidades! Tu oferta por el cómic '{oferta.comic.nombre}' ha sido aceptada."
    )

    return JsonResponse({'success': True, 'message': 'La oferta ha sido aceptada exitosamente'}, status=200)

def rechazar_oferta(request, id_oferta):
    # Obtenemos el usuario que inició sesión
    usuario_contexto = get_usuario(request)
    usuario = usuario_contexto.get('usuario')

    # Verificamos que se haya iniciado sesión
    if usuario is None:
        return JsonResponse({'success': False, 'error': 'Se necesita iniciar sesión para rechazar una oferta'}, status=403)

    # Verificamos que el rol del usuario sea de un vendedor
    if usuario['rol'] != 3:  # Asumimos que el rol 3 corresponde a vendedores
        return JsonResponse({'success': False, 'error': 'Solo los usuarios con rol de vendedor pueden rechazar ofertas'}, status=403)

    # Obtenemos la oferta
    oferta = get_object_or_404(Oferta, id_oferta=id_oferta)

    # Verificamos que el usuario actual sea el receptor de la oferta
    if oferta.receptor.id_usuario != usuario['id']:
        return JsonResponse({'success': False, 'error': 'No puedes rechazar una oferta que no te pertenece'}, status=403)

    # Rechazamos la oferta (establecemos aceptada como False)
    oferta.aceptada = False
    oferta.visto = True
    oferta.save()

    # Creamos un mensaje para el comprador
    Mensaje.objects.create(
        emisor_id=oferta.receptor.id_usuario,  # El vendedor que rechaza
        receptor_id=oferta.emisor.id_usuario,  # El comprador al que se notifica
        contenido=f"Tu oferta por el cómic '{oferta.comic.nombre}' ha sido rechazada."
    )

    # Creamos una notificación para el comprador
    Notificacion.objects.create(
        usuario_id=oferta.emisor.id_usuario,  # El comprador que debe ser notificado
        contenido=f"Tu oferta por el cómic '{oferta.comic.nombre}' ha sido rechazada."
    )

    return JsonResponse({'success': True, 'message': 'La oferta ha sido rechazada exitosamente'}, status=200)

def detalle_oferta(request, id_oferta):
    # Verificamos que la oferta exista
    oferta = get_object_or_404(Oferta, id_oferta=id_oferta)
    contexto = {
        'titulo': 'Detalle de la oferta',
        'oferta': oferta
    }
    return render(request, 'mainapp/detalle_oferta.html', contexto)

    

