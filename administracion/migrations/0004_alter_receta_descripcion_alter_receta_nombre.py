# Generated by Django 4.1.5 on 2024-05-20 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0003_alter_productoreceta_cantidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receta',
            name='descripcion',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='receta',
            name='nombre',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
