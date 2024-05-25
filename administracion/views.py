from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import legal
from reportlab.pdfgen import canvas
from .models import GastosAdicionalesReceta, PasosReceta, Producto, ProductoReceta, Receta
from configuracion.models import Configuracion, Solicitudes
from reportlab.lib.utils import ImageReader
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q,Sum
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
import textwrap


# Función para dibujar texto con salto de línea si es necesario
def draw_text_with_wrapping(p, text, x, y, max_chars_per_line):
    lines = textwrap.wrap(text, width=max_chars_per_line)
    for line in lines:
        p.drawString(x, y, line)
        y -= 15  # Ajustar esta cantidad según el espacio que quieras entre líneas
    return y  # Devuelve la nueva posición y

def custom_bad_request(request, exception):
    return render(request, 'sin_acceso.html', {})#status=400

def descargar(request, id_receta):

    pedido = get_object_or_404(Receta, id=id_receta)
    
    logo_path = pedido.imagen

    #Crear el objeto
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receta_{pedido.nombre}.pdf"'

    # Crear el lienzo PDF
    p = canvas.Canvas(response, pagesize=legal)

    # Agregar contenido al lienzo
    y = 950  # Posición vertical inicial
    x = 50
    
    moneda = Configuracion.objects.first().moneda


    # Verificar si el archivo de imagen del logo existe
    if logo_path:
        # Tamaño y posición del logo
        logo_width = 150  # Ancho del logo
        logo_height = 150 # Alto del logo
        logo_x = 410  # Posición horizontal del logo
        logo_y = 820  # Posición vertical del logo

        # Agregar el logo al lienzo PDF
        logo_image = ImageReader(logo_path)
        p.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)
    

    # nombre
    p.setFont("Helvetica-Bold", 14)  
    p.drawString(x, y, pedido.nombre)
    y -= 25

    # descripcion
    p.setFont("Helvetica", 14)  
    p.drawString(x, y, str(pedido.descripcion).lower())
    y -= 25

    # categoria
    if pedido.categoria:
        p.setFont("Helvetica", 14)  
        p.drawString(x, y, pedido.categoria.nombre)
        y -= 25

    y -= 20

    # Costos de la receta
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Porciones resultantes: ")
    p.setFont("Helvetica", 10)
    p.drawString(180, y, str(pedido.porciones))
    y -= 20

    # Costos de la receta
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Costo total:")
    p.setFont("Helvetica", 10)
    Calculo = pedido.costo_receta()
    codigo_str = str("{:,.2f}".format(Calculo))
    p.drawString(180, y, codigo_str)
    y -= 20

    # Costos de la por porcion
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Costos por porcion:")
    p.setFont("Helvetica", 10)
    Calculo = pedido.costo_porcion()
    codigo_str = str("{:,.2f}".format(Calculo))
    p.drawString(180, y, codigo_str)
    y -= 30


    # Obtener los gastos adicionales de la receta
    gastos_adicionales = GastosAdicionalesReceta.objects.filter(receta=pedido)
    
    cant_gastos = GastosAdicionalesReceta.objects.filter(receta=pedido).count()
    p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
    p.drawString(x, y, f"COSTOS ADICIONALES:")
    y -= 20
    if gastos_adicionales:
        for gasto in gastos_adicionales:
            p.setFont("Helvetica", 10)  # Fuente en negrita
            p.drawString(x, y, f"{gasto.detalle}: {gasto.importe:,.2f}")
            y -= 20

    if cant_gastos <= 1:
        y = 725
    elif cant_gastos <= 3:
        y = 700
    else:
        y = 680
    
    y = 725

    p.setFont("Helvetica-Bold", 11)  # Fuente en negrita y tamaño 14
    p.drawString(x, y, f"ARTICULOS INCLUIDOS:")
    y -= 25

    insumos = ProductoReceta.objects.filter(receta=pedido)
    if insumos:
 
        for insumo in insumos:
            p.setFont("Helvetica-Bold", 9)
            if insumo.producto.descripcion:
                p.drawString(x, y, f"{str(insumo.producto.nombre).upper()} {str(insumo.producto.descripcion).upper()}")
            else:
                p.drawString(x, y, f"{str(insumo.producto.nombre).upper()}")
            y -= 15

            p.setFont("Helvetica", 10)
            p.drawString(x, y, f"({insumo.cantidad} {insumo.medida_uso[:3]}) x ({round(insumo.precio_unitario() or 0,2):,.2f} x {insumo.medida_uso[:3]})  = {round(insumo.precio_total() or 0,2):,.2f}")
            
            y -= 20

    y = 725

    p.setFont("Helvetica-Bold", 11)  # Fuente en negrita y tamaño 14
    p.drawString(x + 250, y , f"PASO A PASO:")
    y -= 25
    
    pasos = PasosReceta.objects.filter(receta=pedido)
    if pasos:

        for paso in pasos:
            
            if paso.nombre:
                p.setFont("Helvetica-Bold", 9)
                p.drawString(x + 250, y - 10, f"{str(paso.nombre).upper()}")

                y -= 25
                p.setFont("Helvetica", 9)
                y = draw_text_with_wrapping(p, f"{str(paso.detalle).upper()}", x + 250, y, 55)
                y -= 20
   
    p.save()

    return response


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            solicitud = Solicitudes.objects.create(usuario=user)
            login(request, user)  # Autentica al usuario automáticamente después del registro
            return redirect('home')  # Redirige a la página de inicio o a donde desees
    else:
        form = CustomUserCreationForm()

    return render(request, 'registro.html', {'form': form})

# @login_required(login_url='/admin/login/')
def home(request):

    configuracion = Configuracion.objects.all().first()

    data = {}

    recetas_publicas_reposteria = Receta.objects.filter(hacer_publico=True,categoria__nombre='REPOSTERIA').order_by('-likes')
    recetas_publicas_panaderia = Receta.objects.filter(hacer_publico=True,categoria__nombre='PANADERIA').order_by('-likes')
    recetas_publicas_desayunos = Receta.objects.filter(hacer_publico=True,categoria__nombre='DESAYUNOS').order_by('-likes')
    recetas_publicas_meriendas = Receta.objects.filter(hacer_publico=True,categoria__nombre='MERIENDAS').order_by('-likes')
    recetas_publicas_unicas = Receta.objects.filter(hacer_publico=True,categoria__nombre='RECETAS UNICAS').order_by('-likes')

    if request.method == 'POST':
        if 'btnsearch' in request.POST:
            search = request.POST['search']
            if not search == '':
                lista_recetas = Receta.objects.filter(
                    Q(nombre__contains=search) | Q(descripcion__contains=search)).distinct()
            else:
                lista_recetas = Receta.objects.order_by('nombre')
            if not lista_recetas:
                data['status'] = 'Sin resultados'


    context = {
        'recetas_publicas_reposteria': recetas_publicas_reposteria, 
        'recetas_publicas_panaderia':recetas_publicas_panaderia,
        'recetas_publicas_desayunos':recetas_publicas_desayunos,
        'recetas_publicas_meriendas':recetas_publicas_meriendas,
        'recetas_publicas_unicas':recetas_publicas_unicas,
        'data': data,
        'configuracion':configuracion}

    return render(request, 'index.html', context)


@login_required(login_url='/admin/login/')
def recetas(request):

    recetas = Receta.objects.all().exclude(hacer_publico=False)

    context = {
        'recetas': recetas,
    }

    return render(request, 'recetas.html', context)

@login_required(login_url='/admin/login/')
def ver(request, id_receta):
    receta = get_object_or_404(Receta, id=id_receta)
    context = {
        'receta': receta,
    }
    return render(request, 'receta_detalle.html', context)

@login_required(login_url='/admin/login/')
def clonar(request, id_receta):

    receta = get_object_or_404(Receta, id=id_receta)

    usuario = request.user

    # Clonar la receta
    receta_clonada = Receta.objects.create(
        nombre=receta.nombre,
        descripcion=receta.descripcion,
        categoria=receta.categoria,
        porciones=receta.porciones,
        rentabilidad=0,
        hacer_publico=False,
        usuario=usuario,
        likes=0
    )

    # Clonar los productos asociados a la receta
    productos = ProductoReceta.objects.filter(receta=receta)
    for producto in productos:
        producto_clonado = Producto.objects.create(
            codigo=producto.producto.codigo,
            nombre=producto.producto.nombre,
            descripcion=producto.producto.descripcion,
            marca=producto.producto.marca,
            unidad_de_medida=producto.producto.unidad_de_medida,
            cantidad=producto.producto.cantidad,
            costo=0,
            usuario=usuario,
        )
        producto_receta = ProductoReceta.objects.create(
            receta=receta_clonada, 
            producto=producto_clonado,
            cantidad=producto.cantidad,
            medida_uso=producto.medida_uso,
            usuario=usuario,
        )
      

    return redirect('home')





