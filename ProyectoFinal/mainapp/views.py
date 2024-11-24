
from .models import Usuario, Rol
from django.contrib import messages
from .forms import FormRegistro, FormLogin
from django.shortcuts import render, redirect
from mainapp.CryptoUtils import cipher, sha256, validate


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
