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
    ),
    path(
        'buscar_comics/',
        views.buscar_comics,
        name='buscar_comics'
    ),
    path('comic/<int:comic_id>/', 
         views.detalle_comic, 
         name='detalle_comic'
        ),
    path(
        'lista_deseos/',
        views.ver_lista_deseos,
        name='ver_lista_deseos'
    ),
    path(
        'lista_deseos/agregar/<int:comic_id>/',
        views.agregar_a_lista_deseos,
        name='agregar_a_lista_deseos'
    ),

    path(
        'lista_deseos/eliminar/<int:comic_id>/', 
         views.eliminar_de_lista_deseos, 
         name='eliminar_deseo'
    ),
    path('hacer_oferta/<int:comic_id>/', 
         views.hacer_oferta, 
         name='hacer_oferta'
    ),
    path('notificaciones/', 
         views.obtener_notificaciones, 
         name='notificaciones'
    ),
    path('marcar-notificacion-vista/<int:oferta_id>/', 
         views.marcar_notificacion_vista, 
         name='marcar_notificacion_vista'
    ),
]