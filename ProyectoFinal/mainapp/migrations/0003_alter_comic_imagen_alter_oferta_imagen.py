# Generated by Django 5.1.1 on 2024-11-24 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_remove_comic_ruta_imagen_remove_oferta_ruta_imagen_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comic',
            name='imagen',
            field=models.ImageField(upload_to='imagenes_comics', verbose_name='Imagen Comic'),
        ),
        migrations.AlterField(
            model_name='oferta',
            name='imagen',
            field=models.ImageField(upload_to='imagenes_trueque', verbose_name='Imagen Objeto o Servicio'),
        ),
    ]