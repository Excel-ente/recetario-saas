# Generated by Django 4.1.5 on 2024-05-25 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracion', '0006_solicitudes'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudes',
            name='fecha_aprobado',
            field=models.DateTimeField(auto_now=True),
        ),
    ]