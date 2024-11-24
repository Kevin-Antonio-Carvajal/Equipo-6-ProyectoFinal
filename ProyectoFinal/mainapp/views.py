
from django.contrib import messages
from django.http import JsonResponse
from .models import Usuario, Rol, Comic
from .forms import FormRegistro, FormLogin
from django.shortcuts import render, redirect
from mainapp.CryptoUtils import cipher, sha256, validate
from mainapp.context_processors import get_usuario


def index(request):

    contexto = {
        'titulo': 'Pagina principal'
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
            return JsonResponse({'success': False, 'error': 'Debes iniciar sesion para registrar un producto'}, status=403)
        # Verificamos el rol del usuario
        if usuario['rol'] != 3:
            return JsonResponse({'success': False, 'error': 'Solo los vendedores pueden registrar un producto'}, status=403)
        # Obtenemos los datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')
        # Validamos la información
        if not nombre or not imagen:
            return JsonResponse({'success': False, 'error': 'El nombre y la imagen son obligatorios'}, status=400)
        # Obtenemos el vendedor
        vendedor = None
        try:
            vendedor = Usuario.objects.get(id_usuario=usuario['id'])
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El vendedor no existe'}, status=404)
        # Creamos el producto
        comic = Comic.objects.create(
            vendedor=vendedor,
            nombre=nombre,
            descripcion=descripcion,
            imagen=imagen
        )
        return JsonResponse({'success': True, 'message': 'Comic registrado exitosamente'}, status=200)
    return JsonResponse({'success': False, 'error': 'Metodo invalido'}, status=400)

def buscar_comics(request):
    # Obtenemos todos los comics, incluida la informacion del vendedor
    comics = Comic.objects.select_related('vendedor').all()
    contexto = {
        'titulo': 'Busqueda de comics',
        'comics': comics
    }
    return render(request, 'mainapp/buscar_comics.html', contexto)