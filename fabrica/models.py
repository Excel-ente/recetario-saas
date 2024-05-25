# -----------------------------------------------------------------------------
# Project Programacion para mortales
# Desarrollador : Kevin Turkienich
# 2024
# -----------------------------------------------------------------------------
# APP para calcular el costo y manejar diferentes recetas

# -----------------------------------------------------------------------------
# Listas para unidad de medida de producto
UNIDADES_DE_MEDIDA = [
    ('Unidades', 'Unidades'),
    ('Kilos', 'Kilos'),
    ('Gramos', 'Gramos'),
    ('Litros', 'Litros'),
    ('Mililitros', 'Mililitros'),
    ('Mt2s', 'Mt2s'),
    ('Onzas', 'Onzas'),
    ('Libras', 'Libras'),
]

# -----------------------------------------------------------------------------
# Importaciones

from django.db import models
from django.core.exceptions import ValidationError
from administracion.models import Receta
# -----------------------------------------------------------------------------
# Modulo de categorias de productos
class Lotes(models.Model):
    """ Modelo que representa una fabricacion de productos. """
    codigo = models.CharField(max_length=100)
    fecha_fabricacion = models.DateField(null=False, blank=False)
    fecha_vencimiento = models.DateField(null=False, blank=False)
    estado = models.BooleanField(default=False)
    usuario = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'{self.fecha_fabricacion} | {self.id}'
    
    def clean(self):
        # Validación para asegurar que el usuario no edite registros de otros usuarios
        if self.pk and self.usuario != self.usuario:
            raise ValidationError('No puedes editar registros que no te pertenecen.')

    class Meta:
        verbose_name = 'lote'
        verbose_name_plural = 'Fabricaciones'
# -----------------------------------------------------------------------------
# Modulo de categorias de productos
class LotesProducto(models.Model):
    """ Modelo que representa un item de una fabricacion. """
    lote = models.ForeignKey(Lotes,on_delete=models.CASCADE,blank=False,null=False)
    receta = models.ForeignKey(Receta,on_delete=models.CASCADE,blank=False,null=False)
    cantidad = models.FloatField(null=False, blank=False,default=1)
    usuario = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'{self.receta} x {self.cantidad}'
    
    def clean(self):
        # Validación para asegurar que el usuario no edite registros de otros usuarios
        if self.pk and self.usuario != self._current_user:
            raise ValidationError('No puedes editar registros que no te pertenecen.')