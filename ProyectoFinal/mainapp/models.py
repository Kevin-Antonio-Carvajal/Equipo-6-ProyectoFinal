from django.db import models

# TABLA ROL
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=32, unique=True)
    # administrador: id 1    
    # comprador: id 2
    # vendedor: id: 3
    def __str__(self):
        return self.nombre

# TABLA USUARIO
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name="usuarios")
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

# TABLA COMIC
class Comic(models.Model):
    id_comic = models.AutoField(primary_key=True)
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="comics")
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    ruta_imagen = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

# TABLA OFERTA
class Oferta(models.Model):
    id_oferta = models.AutoField(primary_key=True)
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="ofertas_enviadas")
    receptor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="ofertas_recibidas")
    objeto = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    servicio = models.BooleanField(default=False)
    aceptada = models.BooleanField(null=True, blank=True)  # NULL significa que aún no se ha decidido
    visto = models.BooleanField(default=False)
    ruta_imagen = models.TextField()
    fecha_emision = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Oferta {self.id_oferta} - {self.objeto}"

# TABLA MENSAJE
class Mensaje(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensajes_enviados")
    receptor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensajes_recibidos")
    fecha_emision = models.DateTimeField(auto_now_add=True)
    visto = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.emisor} a {self.receptor}"
