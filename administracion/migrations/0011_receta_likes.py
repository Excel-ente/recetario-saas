# Generated by Django 4.1.5 on 2024-05-22 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0010_receta_hacer_publico'),
    ]

    operations = [
        migrations.AddField(
            model_name='receta',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]