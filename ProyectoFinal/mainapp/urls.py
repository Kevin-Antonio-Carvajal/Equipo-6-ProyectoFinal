from django.urls import path
from . import views

urlpatterns = [
    path(
        '',             # Ruta
        views.index,    # Vista
        name='inicio'   # Nombre
    ),
    path(
        'inicio/',
        views.index,
        name='inicio'
    )
]