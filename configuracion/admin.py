# Administrador de Django - Configuraciones generales

# importaciones
from django.contrib import messages
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Configuracion, Solicitudes

# -----------------------------------------------------------------------------
# # Registro del modelo GastosAdicionalesReceta en el admin de Django

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    exclude = ('usuario',)

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
            return ('id','nombre_emprendimiento','telefono','redes_sociales','moneda','usuario')
        return ('id','nombre_emprendimiento','telefono','redes_sociales','moneda',)
    
    
    def get_list_filter(self, request):
        # Mostrar el campo 'usuario' solo a los superusuarios
        if request.user.is_superuser:
            return  ('id','nombre_emprendimiento', 'moneda','usuario')
        return   ('id','nombre_emprendimiento', 'moneda')
    
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# # Registro del modelo GastosAdicionalesReceta en el admin de Django


@admin.register(Solicitudes)
class SolicitudesAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'aprobado',)
    readonly_fields = ('fecha','fecha_aprobado',)

    @admin.action(description="autorizar")
    def autorizar(modeladmin, request, queryset):
        
        if request.user.groups.filter(name='Aprobadores').exists():
            for query in queryset:
                if not query.aprobado:
              
                    # Obtener el grupo "user_base"
                    user_base_group = Group.objects.get(name='user_base')
                    # Asignar el usuario al grupo "user_base"
                    query.usuario.groups.add(user_base_group)

                    query.aprobado = True
                    query.save()


            messages.success(request, "La/s Solicitud/es fueron aprobadas correctamente.")
        else:
            messages.error(request, "No tienes permisos para aprobar estas solicitudes.")

    actions = [autorizar,]

    def get_queryset(self, request):
        # Filtrar los registros para que el usuario solo vea los que él ha creado
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(aprobado=False)


# -----------------------------------------------------------------------------
