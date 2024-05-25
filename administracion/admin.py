from django.contrib import admin
from .models import Categoria, PasosReceta, Producto, Receta, GastosAdicionalesReceta, ProductoReceta, CategoriaReceta
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields, widgets
from configuracion.models import Configuracion
from .Reporte import generar_presupuesto
from django.utils.html import format_html
from django.urls import reverse

# -----------------------------------------------------------------------------
# # Herramienta para configurar el reporte de descarga de la receta
         
class RecetaResource(resources.ModelResource):

        nombre = fields.Field(attribute='nombre', column_name='nombre')
        descripcion = fields.Field(attribute='descripcion',  column_name='descripcion')
        categoria = fields.Field(attribute='categoria', column_name='categoria', widget=widgets.ForeignKeyWidget(CategoriaReceta, 'nombre'))
        porciones = fields.Field(attribute='porciones', column_name='porciones')
        rentabilidad = fields.Field(attribute='rentabilidad',  column_name='rentabilidad')
        comentarios= fields.Field(attribute='comentarios', column_name='comentarios')
        costo_receta = fields.Field(column_name='costo_receta')
        costo_porcion = fields.Field(column_name='costo_porcion')
        precio_venta_porcion = fields.Field(column_name='precio_venta_porcion')
        precio_venta_total = fields.Field(column_name='precio_venta_total')

        class Meta:
                model = Receta

        def dehydrate_costo_receta(self, receta):
            return receta.costo_receta()

        def dehydrate_costo_porcion(self, receta):
            return receta.costo_porcion()
        
        def dehydrate_precio_venta_porcion(self, receta):
            valor = receta.precio_venta_porcion or 0
            return valor

        def dehydrate_precio_venta_total(self, receta):
            valor = receta.precio_venta_total or 0
            return valor

# -----------------------------------------------------------------------------
# # Herramienta para configurar el reporte de descarga del producto
         
class ProductoResource(resources.ModelResource):

        codigo = fields.Field(attribute='codigo',  column_name='codigo')
        nombre = fields.Field(attribute='nombre', column_name='nombre')
        descripcion = fields.Field(attribute='descripcion',  column_name='descripcion')
        categoria = fields.Field(attribute='categoria', column_name='categoria', widget=widgets.ForeignKeyWidget(Categoria, 'nombre'))
        marca = fields.Field(attribute='marca', column_name='marca')
        unidad_de_medida = fields.Field(attribute='unidad_de_medida',  column_name='unidad_de_medida')
        cantidad= fields.Field(attribute='cantidad', column_name='cantidad')
        costo= fields.Field(attribute='costo', column_name='costo')
        
        class Meta:
                model = Producto


        def before_import_row(self, row, **kwargs):
            # Assign the user to the row data
            row['usuario'] = kwargs['user']
        
# -----------------------------------------------------------------------------
# # Herramienta para configurar el reporte de descarga del producto
         
class ProductoRecetaResource(resources.ModelResource):

        # producto = fields.Field(attribute='producto', column_name='producto',)# widget=widgets.ForeignKeyWidget(Producto, 'codigo'))
        # receta = fields.Field(attribute='receta', column_name='receta', )#widget=widgets.ForeignKeyWidget(Receta, 'nombre'))
        # unidad_de_medida = fields.Field(attribute='unidad_de_medida',  column_name='unidad_de_medida')
        # cantidad= fields.Field(attribute='cantidad', column_name='cantidad')

        class Meta:
                model = ProductoReceta

        def before_import_row(self, row, **kwargs):
            # Assign the user to the row data
            row['usuario'] = kwargs['user']
        

# -----------------------------------------------------------------------------
# # Registro del modelo GastosAdicionalesReceta en el admin de Django

@admin.register(CategoriaReceta)
class CategoriaRecetaAdmin(ImportExportModelAdmin):
    exclude = ('usuario',)
    list_display_links = ('id','nombre',)
    search_fields = ('nombre',)
    list_per_page = 15

    def get_queryset(self, request):
        # Filtrar los registros para que el usuario solo vea los que él ha creado
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el usuario al registro
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return ('id','nombre', 'usuario')
        return ('id','nombre',)
    
    def get_list_filter(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return   ('id','usuario',)
        return   ('id',)
# -----------------------------------------------------------------------------
# Registro del modelo Categoria en el admin de Django

@admin.register(Categoria)
class CategoriaAdmin(ImportExportModelAdmin):
    exclude = ('usuario',)
    list_filter=('usuario',)
    search_fields = ('nombre',)
    list_per_page = 15
    list_display_links = ('id','nombre',)

    def get_queryset(self, request):
        # Filtrar los registros para que el usuario solo vea los que él ha creado
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el usuario al registro
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return ('id','nombre', 'usuario')
        return ('id','nombre',)
    
    def get_list_filter(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return   ('id','usuario',)
        return   ('id',)

# -----------------------------------------------------------------------------
# Inline para ProductoReceta, para ser usado dentro del admin de Receta

class PasosRecetaInline(admin.StackedInline):
    model = PasosReceta
    extra = 0  # Número de formularios vacíos adicionales que se muestran
    fields = ('nombre','detalle')
    exclude = ('usuario',)
    
# -----------------------------------------------------------------------------
# Inline para ProductoReceta, para ser usado dentro del admin de Receta

class ProductoRecetaInline(admin.StackedInline):
    model = ProductoReceta
    extra = 0  # Número de formularios vacíos adicionales que se muestran
    readonly_fields = ('Subtotal',)
    exclude = ('usuario',)

    # metodo para calcular el subtotal
    def Subtotal(self, obj):
        moneda = Configuracion.objects.first().moneda
        costo_total = float(obj.precio_total())
        return f'{moneda} {costo_total:,.2f}'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "producto":
            # Filtrar las categorías basadas en el usuario actual
            kwargs["queryset"] = Producto.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
# -----------------------------------------------------------------------------
# Inline para GastosAdicionalesReceta, para ser usado dentro del admin de Receta
class GastosAdicionalesRecetaInline(admin.TabularInline):
    model = GastosAdicionalesReceta
    extra = 0  # Número de formularios vacíos adicionales que se muestran
    exclude = ('usuario',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "receta":
            # Filtrar las categorías basadas en el usuario actual
            kwargs["queryset"] = Receta.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
# -----------------------------------------------------------------------------
# Registro del modelo Producto en el admin de Django


@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    list_display = ('id','nombre','categoria','Cantidad','unidad_de_medida','Costo','Costo_Unitario')
    list_display_links = ('id', 'nombre','categoria','Cantidad','unidad_de_medida','Costo','Costo_Unitario')
    search_fields = ('nombre', 'marca')
    list_filter = ('id','codigo','categoria', 'unidad_de_medida','usuario')
    resource_class = ProductoResource
    exclude = ('usuario',)
    list_per_page = 15

    def Costo_Unitario(self,obj):
        moneda = Configuracion.objects.first().moneda
        return f'{moneda} {obj.costo_unitario():,.2f}'

    def Costo(self,obj):
          moneda = Configuracion.objects.first().moneda
          return f'{moneda} {obj.costo:,.2f}'

    def Cantidad(self,obj):
          return f'{obj.cantidad:,.2f}'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "categoria":
            # Filtrar las categorías basadas en el usuario actual
            kwargs["queryset"] = Categoria.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        # Filtrar los registros para que el usuario solo vea los que él ha creado
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el usuario al registro
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return ('nombre','Cantidad','unidad_de_medida','Costo','usuario')
        return ('nombre','Cantidad','unidad_de_medida','Costo',)

    def get_list_filter(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return   ('id','codigo','categoria', 'unidad_de_medida','usuario')
        return   ('id','codigo','categoria', 'unidad_de_medida',)
    
# -----------------------------------------------------------------------------
# Registro del modelo Receta en el admin de Django
@admin.register(Receta)
class RecetaAdmin(ImportExportModelAdmin):
    list_display = ('id','nombre',  'porciones', 'Costo_porcion','Costo_total','Descargar')
    list_display_links = ('nombre',  'porciones''Costo_porcion','Costo_total')
    list_filter = ('id','categoria','porciones','usuario',)
    search_fields = ('nombre',)
    inlines = [ ProductoRecetaInline, GastosAdicionalesRecetaInline, PasosRecetaInline,]
    resource_class = RecetaResource
    actions = [generar_presupuesto,]
    exclude = ('usuario',)
    list_per_page = 15

    # metodo para calcular el subtotal
    def Costo_porcion(self, obj):
        moneda = Configuracion.objects.first().moneda
        costo_total = float(obj.costo_porcion())
        return f'{moneda} {costo_total:,.2f}'
    
    # metodo para calcular el subtotal
    def Costo_total(self, obj):
        moneda = Configuracion.objects.first().moneda
        costo_total = float(obj.costo_receta())
        return f'{moneda} {costo_total:,.2f}'


    # método para botón de descargar
    def Descargar(self, obj):
        return format_html('<a class="btn btn-secondary" href="{}">⬇️ PDF', reverse('descargar', args=[obj.id]))
    Descargar.short_description = "Acciones"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "categoria":
            # Filtrar las categorías basadas en el usuario actual
            kwargs["queryset"] = CategoriaReceta.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        # Filtrar los registros para que el usuario solo vea los que él ha creado
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el usuario al registro
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return ('id','nombre','rentabilidad','Costo_total','Descargar','usuario')
        return ('nombre','Costo_total','Descargar',)

    def get_list_filter(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return  ('id','categoria','porciones','usuario',)
        return  ('id','categoria','porciones',)
# # -----------------------------------------------------------------------------
# # Registro del modelo Producto receta en el admin de Django
@admin.register(ProductoReceta)
class ProductoRecetaAdmin(ImportExportModelAdmin):
    list_display = ('producto', 'receta','Cantidad','medida_uso','Costo_Unitario','Total',)
    readonly_fields = ('producto', 'receta','Cantidad','medida_uso','Costo_Unitario','Total',)
    exclude = ( 'receta''medida_uso','usuario','cantidad','producto',)
    search_fields = ('codigo', 'nombre', 'marca')
    list_filter = ('producto__nombre', 'receta')
    resource_class = ProductoRecetaResource
    list_per_page = 15

    def Producto(self,obj):
        return f'{obj.producto.nombre} {obj.producto.descripcion}'

    def Costo_Unitario(self,obj):
        moneda = Configuracion.objects.first().moneda
        return f'{moneda} {obj.precio_unitario():,.2f}'

    def Total(self,obj):
        moneda = Configuracion.objects.first().moneda
        return f'{moneda} {obj.precio_total():,.2f}'

    def Cantidad(self,obj):
        return f'{obj.cantidad:,.2f}'


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "producto":
            # Filtrar las categorías basadas en el usuario actual
            kwargs["queryset"] = Producto.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "receta":
            # Filtrar las categorías basadas en el usuario actual
            kwargs["queryset"] = Receta.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
     
    def get_queryset(self, request):
        # Filtrar los registros para que el usuario solo vea los que él ha creado
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el usuario al registro
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return('Producto', 'receta','Cantidad','medida_uso','Costo_Unitario','Total','usuario')
        return ('Producto', 'receta','Cantidad','medida_uso','Costo_Unitario','Total',)
    
    
    def get_list_filter(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return  ('id','producto__nombre', 'receta','usuario')
        return   ('id','producto__nombre', 'receta')
    