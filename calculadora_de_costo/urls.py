from django.contrib import admin
from django.urls import include, path
from administracion.views import descargar, home, custom_bad_request,register,recetas,ver,clonar
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler400, handler404

handler400 = custom_bad_request
handler404 = custom_bad_request

urlpatterns = [
    path('', home, name='home'),
    path('registro/', register, name='registro'),
    path('descargar/<int:id_receta>/', descargar, name='descargar'),
    path('clonar/<int:id_receta>/', clonar, name='clonar'),
    path('admin/', admin.site.urls ,name='admin'),
    path('recetas/', recetas ,name='recetas'),
    path('ver/<int:id_receta>/', ver, name='ver'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
