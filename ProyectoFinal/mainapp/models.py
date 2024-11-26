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
    imagen = models.ImageField(verbose_name='Imagen Comic', upload_to='imagenes_comics')
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

# TABLA OFERTA
class Oferta(models.Model):
    id_oferta = models.AutoField(primary_key=True)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, null=True, blank=True, related_name="ofertas")
    receptor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="ofertas_recibidas")    
    objeto = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    servicio = models.BooleanField(default=False)
    aceptada = models.BooleanField(null=True, blank=True)  # NULL significa que aún no se ha decidido
    visto = models.BooleanField(default=False)
    imagen = models.ImageField(verbose_name='Imagen Objeto o Servicio', upload_to='imagenes_trueque')
    fecha_emision = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Oferta {self.id_oferta} - {self.objeto}"

# TABLA VENTA
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    comic = models.OneToOneField(Comic, on_delete=models.CASCADE, related_name="venta")  # Relación directa con el cómic vendido
    comprador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="ventas_recibidas")
    oferta = models.OneToOneField(Oferta, on_delete=models.CASCADE, null=True, blank=True, related_name="venta")  # Relacionar con la oferta aceptada
    fecha_venta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comic.nombre} vendido por {self.comic.vendedor.username} a {self.comprador.username}"


# TABLA MENSAJE
class Mensaje(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensajes_enviados")
    receptor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensajes_recibidos")
    fecha_emision = models.DateTimeField(auto_now_add=True)
    visto = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.emisor} a {self.receptor}"

class ListaDeseos(models.Model):
    id_lista = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="listas_deseos")
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="en_listas_deseos")
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'comic') 

    def __str__(self):
        return f"{self.usuario.username} - {self.comic.nombre}"