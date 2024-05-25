from django.contrib import admin
from .models import Lotes,LotesProducto
from import_export.admin import ImportExportModelAdmin
from administracion.models import Receta


# -----------------------------------------------------------------------------
# Inline para ProductoReceta, para ser usado dentro del admin de Receta

class LotesProductoInline(admin.StackedInline):
    model = LotesProducto
    extra = 0  # Número de formularios vacíos adicionales que se muestran
    fields = ('receta','cantidad',)
    exclude = ('usuario',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "receta":
            # Filtrar las categorías basadas en el usuario actual
            kwargs["queryset"] = Receta.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# # Registro del modelo GastosAdicionalesReceta en el admin de Django

@admin.register(Lotes)
class LotesAdmin(ImportExportModelAdmin):
    list_display_links = ('fecha_fabricacion','fecha_vencimiento','estado')
    list_display = ('fecha_fabricacion','fecha_vencimiento','estado')
    exclude = ('usuario','estado')
    readonly_fields = ('codigo',)
    list_filter=('usuario','codigo',)
    search_fields = ('codigo',)
    inlines = [LotesProductoInline,]

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
            return ('codigo','fecha_fabricacion','fecha_fabricacion','fecha_vencimiento','estado','usuario')
        return ('codigo','fecha_fabricacion','fecha_fabricacion','fecha_vencimiento','estado','usuario')

