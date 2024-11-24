from django.contrib import admin
from .models import Rol, Usuario, Comic, Oferta, Mensaje

# Configuracion para mostrar los modelos en el panel de administracion
class UsuarioAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_usuario',
        'created_at'
    )
    # Campos que no queremos que se muestren
    exclude = ('password',)

# Configuracion para mostrar los modelos en el panel de administracion
class RolAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_rol',        
    )

# Configuracion para mostrar los modelos en el panel de administracion
class ComicAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_comic',
        'vendedor',
        'created_at'
    )

# Configuracion para mostrar los modelos en el panel de administracion
class OfertaAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_oferta',
        'emisor',
        'receptor',
        'fecha_emision'
    )

# Configuracion para mostrar los modelos en el panel de administracion
class MensajeAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_mensaje',
        'emisor',
        'receptor',
        'fecha_emision'        
    )

# Agregamos al panel de administracion
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Rol, RolAdmin)
admin.site.register(Comic, ComicAdmin)
admin.site.register(Oferta, OfertaAdmin)
admin.site.register(Mensaje, MensajeAdmin)