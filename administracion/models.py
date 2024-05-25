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
from django.core.validators import FileExtensionValidator

# -----------------------------------------------------------------------------
# Validacion para que la imagen sea de 500 x 500 pixeles
def validate_image_size(value):
    """ Valida que la imagen tenga un tamaño de 500x500 píxeles. """
    width, height = value.width, value.height
    if width != 500 or height != 500:
        raise ValidationError('La imagen debe ser de 500x500 píxeles.')

# -----------------------------------------------------------------------------
# Modulo de categorias de productos
class CategoriaReceta(models.Model):
    """ Modelo que representa una categoría de productos. """
    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
    def clean(self):
        # Validación para asegurar que el usuario no edite registros de otros usuarios
        if self.pk and self.usuario != self._current_user:
            raise ValidationError('No puedes editar registros que no te pertenecen.')
    
# -----------------------------------------------------------------------------
# Modulo de categorias de productos
class Categoria(models.Model):
    """ Modelo que representa una categoría de productos. """
    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        # Validación para asegurar que el usuario no edite registros de otros usuarios
        if self.pk and self.usuario != self._current_user:
            raise ValidationError('No puedes editar registros que no te pertenecen.')
# -----------------------------------------------------------------------------
# Modulo de productos
class Producto(models.Model):
    """ Modelo que representa un producto con sus detalles. """
    codigo = models.CharField(max_length=20, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=False, null=False)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.CharField(max_length=200, blank=True, null=True)
    unidad_de_medida = models.CharField(max_length=50, choices=UNIDADES_DE_MEDIDA, blank=False, null=False, default="Unidades")
    cantidad = models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    costo = models.FloatField(default=0, blank=True, null=True)
    usuario = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'{self.nombre} x {self.cantidad} {self.unidad_de_medida} | costo unitario {self.costo_unitario():,.2f}'

    def costo_unitario(self):
        """ Calcula el costo unitario del producto. """
        return float(self.costo) / float(self.cantidad)

    def clean(self):
        if self.costo < 0:
            raise ValidationError("El costo no puede ser menor a 0.")
        
        if not self.pk and Receta.objects.count() >= 50:
            raise ValidationError("Alcanzaste el máximo de insumos.")
        
# -----------------------------------------------------------------------------
# Modulo de recetas
class Receta(models.Model):
    """ Modelo que representa una receta con sus detalles. """
    imagen = models.ImageField(
        upload_to='img/recetas/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']), validate_image_size]
    )
    nombre = models.CharField(max_length=150,  blank=False, null=False,)
    descripcion = models.CharField(max_length=150,blank=False, null=False)
    categoria = models.ForeignKey(CategoriaReceta, on_delete=models.SET_NULL, null=True, blank=True)
    porciones = models.DecimalField(max_digits=15, decimal_places=2, default=1, blank=False, null=False)
    rentabilidad = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=False, null=False)
    comentarios = models.TextField(null=True, blank=True)
    hacer_publico=models.BooleanField(default=False)
    usuario = models.CharField(max_length=120, null=True, blank=True)
    likes = models.IntegerField(default=0,blank=False,null=False)

    def __str__(self):
        return f'{self.nombre}'

    class Meta:
        verbose_name = 'receta'
        verbose_name_plural = 'Recetas'

    def costo_receta(self):
        """ Calcula el costo total de la receta sumando el costo de los productos, subrecetas y gastos adicionales. """

        total_productos = 0

        # Sumar gastos adicionales
        adicionales = GastosAdicionalesReceta.objects.filter(receta=self)
        suma_adicionales = sum(float(adicional.importe) if adicional.importe is not None else 0 for adicional in adicionales)

        # Sumar costos de los productos en la receta
        productos = ProductoReceta.objects.filter(receta=self)
        for producto in productos:
            total_productos += producto.precio_total()

        # Calcular el costo total
        total = suma_adicionales + total_productos

        return total

    def costo_porcion(self):
        """ Calcula el costo por porción de la receta. """
        total = float(self.costo_receta())
        return total / float(self.porciones)

    @staticmethod
    def precio_venta_porcion(self):
        """ Calcula el precio por porción de la receta. """
        total = float(float(self.costo_porcion())/ float(100 - self.rentabilidad) * 100)
        return  total

    @staticmethod
    def precio_venta_total(self):
        """ Calcula el precio total de la receta. """
        total = float(self.precio_venta_porcion()) * float(self.porciones)
        return total

    def clean(self):
        if self.rentabilidad < 0:
            raise ValidationError("La rentabilidad no puede ser negativa.")
  
# -----------------------------------------------------------------------------
# Modulo de gastos adicionales de receta
class GastosAdicionalesReceta(models.Model):
    """ Modelo que representa los gastos adicionales de una receta. """
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    detalle = models.CharField(max_length=50, blank=False, null=False)
    importe = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    usuario = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        verbose_name = 'gasto'
        verbose_name_plural = 'Gastos adicionales'

    def __str__(self):
        return str(self.detalle)

    def clean(self):
        """ Valida que el importe del gasto adicional sea mayor que 0. """
        if self.importe <= 0:
            raise ValidationError("El importe del gasto adicional no puede ser inferior o igual a $ 0.")
        super().clean()

# -----------------------------------------------------------------------------
# Modulo producto<>receta 
# Este modulo, se utiliza como relacion intermedia entre el producto y la receta
class ProductoReceta(models.Model):
    """ Modelo que representa la relación entre un producto y una receta, incluyendo la cantidad y la medida de uso. """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    medida_uso = models.CharField(max_length=50, choices=UNIDADES_DE_MEDIDA, blank=False, null=False, default="Unidades")
    usuario = models.CharField(max_length=120, null=True, blank=True)
    
    def save(self, *args, **kwargs): 
        if not self.usuario:
            self.usuario = self.receta.usuario
        super(ProductoReceta, self).save(*args, **kwargs)
    

    class Meta:
        verbose_name = 'producto incluido'
        verbose_name_plural = 'Productos incluidos'

    def __str__(self):
        return str(self.producto.nombre)

    def clean(self):
        """ Valida que la cantidad y la unidad de medida sean correctas. """
        if self.cantidad <= 0:
            raise ValidationError("Por favor ingrese una cantidad superior a 0.")

        if self.producto.unidad_de_medida == 'Unidades' and self.medida_uso != 'Unidades':
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Unidades'.")

        if self.producto.unidad_de_medida == 'Mt2s' and self.medida_uso != 'Mt2s':
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Mt2s'.")

        if self.producto.unidad_de_medida == 'Kilos' and self.medida_uso not in ['Kilos', 'Gramos']:
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Kilos' o 'Gramos'.")

        if self.producto.unidad_de_medida == 'Litros' and self.medida_uso not in ['Litros', 'Mililitros']:
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Litros' o 'Mililitros'.")

        if self.producto.unidad_de_medida == 'Gramos' and self.medida_uso not in ['Kilos', 'Gramos']:
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Kilos' o 'Gramos'.")

        if self.producto.unidad_de_medida == 'Mililitros' and self.medida_uso not in ['Litros', 'Mililitros']:
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Litros' o 'Mililitros'.")

        if self.producto.unidad_de_medida == 'Onzas' and self.medida_uso not in ['Onzas', 'Libras']:
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Onzas' o 'Libras'.")

        if self.producto.unidad_de_medida == 'Libras' and self.medida_uso not in ['Onzas', 'Libras']:
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Onzas' o 'Libras'.")

    def precio_unitario(self):
        total = 0
        if self.producto.unidad_de_medida != self.medida_uso:
            if self.producto.unidad_de_medida == "Litros" or self.producto.unidad_de_medida == "Kilos":
                total = (float(self.producto.costo_unitario()) / 1000) 
            if self.producto.unidad_de_medida == "Gramos" or self.producto.unidad_de_medida == "Mililitros":
                total = (float(self.producto.costo_unitario()) * 1000) 
            elif  self.producto.unidad_de_medida == "Libras":
                total = (float(self.producto.costo_unitario()) / 16)
            elif  self.producto.unidad_de_medida == "Onzas":
                total = (float(self.producto.costo_unitario()) / 0.0625) 
        else:
            total = float(self.producto.costo_unitario()) 

        return total

    def precio_total(self):
        """ Calcula el costo total del producto en la receta. """
        return self.precio_unitario() * float(self.cantidad)


# -----------------------------------------------------------------------------
# Modulo producto<>receta 
# Este modulo, se utiliza como relacion intermedia entre el producto y la receta
class PasosReceta(models.Model):
    """ Modelo que representa la relación entre un producto y una receta, incluyendo la cantidad y la medida de uso. """
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255,blank=False,null=False)
    detalle = models.TextField(blank=False, null=False)
    usuario = models.CharField(max_length=120, null=True, blank=True)
    
    def save(self, *args, **kwargs): 
        if not self.usuario:
            self.usuario = self.receta.usuario
        super(PasosReceta, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'pasos'
        verbose_name_plural = 'Pasos'

    def __str__(self):
        return str(self.nombre)

# -----------------------------------------------------------------------------