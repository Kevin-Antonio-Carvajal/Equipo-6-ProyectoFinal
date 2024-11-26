# Generated by Django 5.1.3 on 2024-11-26 00:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_comic_precio'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListaDeseos',
            fields=[
                ('id_lista', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_agregado', models.DateTimeField(auto_now_add=True)),
                ('comic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='en_listas_deseos', to='mainapp.comic')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listas_deseos', to='mainapp.usuario')),
            ],
            options={
                'unique_together': {('usuario', 'comic')},
            },
        ),
    ]