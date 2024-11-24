from django.urls import path
from . import views

urlpatterns = [
    path(
        '',             # Ruta
        views.index,    # Vista
        name='index'   # Nombre
    ),
    path(
        'inicio/',
        views.index,
        name='inicio'
    ),
    path(
        'register/',
        views.register,
        name='register'
    ),
    path(
        'login/',
        views.login,
        name='login'
    ),
    path(
        'logout/',
        views.logout,
        name='logout'
    ),
    path(
        'registrar_comic/',
        views.registrar_comic,
        name='registrar_comic'
    ),
    path(
        'crear_comic/',
        views.crear_comic,
        name='crear_comic'
    )
]