# Proyecto Final Equipo 6

**Repositorio** https://github.com/Kevin-Antonio-Carvajal/Equipo-6-ProyectoFinal

# Aplicación de compra y venta de comics por trueque

## Profesor:

- Dario Emmanuel Vázquez Ceballos

## Ayudantes:

- Alejandro Gónzalez Ruíz
- Andrea Uxue Amaya Navarrete
- María Fernanda Mendoza Castillo

## Alumnos:

- Arrieta Mancera Luis Sebastian
- Antonio Carvajal Kevin
- Morales Hidalgo Pedro
- Mendiola Montes Victor Manuel
- García Zárraga Angélica Lizbeth
- Rodríguez García Ulises
- 
# Super Usuarios

Comando para crear super-usuarios:

```bash
python3 manage.py createsuperuser
```

## Ejemplo:

**Usuario:** sebs

**Correo:** sebastian_luis@ciencias.unam.mx

# Ayuda
En caso de que los estilos CSS no se vean reflejados en la página, presiona `Ctrl+F5`, esto sucede porque el navegador guarda los estilos css en caché.

# Ejecución

Instala las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

Ejecuta el proyecto ejecutando el archivo `manage.py` con el siguiente comando:

```bash
python3 manage.py runserver
```

La base de datos ya cuenta con lo necesario para comenzar a interactuar con el proyecto, solo create un usuario como comprador o vendedor. Los vendedores pueden crear comics, mientras que los compradores pueden mandar ofertas, si no has iniciado sesion no podrás mandar ofertas, ni siquiera te aparecerá la opcion.
