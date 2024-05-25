# -----------------------------------------------------------------------------
# Project Programacion para mortales
# Desarrollador : Kevin Turkienich
# 2024
# -----------------------------------------------------------------------------
# APP para calcular el costo y manejar diferentes recetas

# -----------------------------------------------------------------------------
# Importaciones

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# -----------------------------------------------------------------------------
# Modulo de configuracion
class Configuracion(models.Model):
    """ Modelo para configuraciones generales """
    nombre_emprendimiento = models.CharField(max_length=20, blank=False, null=False)
    telefono = models.CharField(max_length=100, blank=True, null=True)
    redes_sociales = models.CharField(max_length=200, blank=True, null=True)
    moneda = models.CharField(max_length=200, blank=False, null=False,default='$')
    logo = models.ImageField(blank=True,null=True)
    licencia = models.CharField(max_length=120, blank=True, null=True)
    mostrar_foto = models.BooleanField(default=True)
    usuario = models.CharField(max_length=120, null=True, blank=True)
    
    def __str__(self):
        return f'{self.nombre_emprendimiento}'
    

# -----------------------------------------------------------------------------
# Modulo de configuracion
class Solicitudes(models.Model):
    """ Modelo para configuraciones generales """
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    aprobado = models.BooleanField(default=False)
    fecha_aprobado = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.fecha} | {self.usuario}'


    def clean(self):
        if self.aprobado:
            raise ValidationError("Las solicitudes aprobadas no pueden ser modificadas.")
        
    def save(self, *args, **kwargs):
        if self.pk:
            user=self.usuario
            empresa=Configuracion.objects.create(
                nombre_emprendimiento=f'Mi emprendimiento',
                usuario=user, 
            )

        super().save(*args, **kwargs)

# -----------------------------------------------------------------------------
