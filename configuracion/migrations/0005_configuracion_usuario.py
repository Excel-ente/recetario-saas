# Generated by Django 4.1.5 on 2024-05-24 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracion', '0004_configuracion_mostrar_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracion',
            name='usuario',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
