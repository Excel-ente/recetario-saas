# Generated by Django 4.1.5 on 2024-05-20 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracion', '0002_configuracion_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracion',
            name='licencia',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]