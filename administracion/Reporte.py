from django.http import HttpResponse
from reportlab.lib.pagesizes import legal
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from django.contrib import admin, messages
from .models import GastosAdicionalesReceta,ProductoReceta
from configuracion.models import Configuracion


@admin.action(description="Descargar Receta")
def generar_presupuesto(modeladmin, request, queryset):

    #Validacion para que seleccione solo 1 queryset
    if len(queryset) != 1:
        messages.error(request, "Seleccione solo una receta para generar el informe.")
        return
      
    # Obtener el primer pedido seleccionado
    pedido = queryset[0]
    
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
        logo_width = 100  # Ancho del logo
        logo_height = 100 # Alto del logo
        logo_x = 410  # Posición horizontal del logo
        logo_y = 820  # Posición vertical del logo

        # Agregar el logo al lienzo PDF
        logo_image = ImageReader(logo_path)
        p.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)
    

    # nombre
    p.setFont("Helvetica-Bold", 13)  
    p.drawString(x, y, pedido.nombre)
    y -= 25

    # descripcion
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(x, y, str(pedido.descripcion).lowwer())
    y -= 25

    # categoria
    if pedido.categoria:
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(x, y, pedido.categoria.nombre)

    y -= 25


    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Porciones resultantes: ")
    p.setFont("Helvetica", 10)
    p.drawString(150, y, pedido.porciones)
    y -= 25


    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Costos totales: $ ")
    p.setFont("Helvetica", 10)
    Calculo = pedido.costo_receta()
    codigo_str = str("{:,.2f}".format(Calculo))
    p.drawString(140, y, codigo_str)
    y -= 25

    # Costos de la por porcion
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Costos por porcion: $ ")
    p.setFont("Helvetica", 10)
    Calculo = pedido.costo_porcion()
    codigo_str = str("{:,.2f}".format(Calculo))
    p.drawString(180, y, codigo_str)
    y -= 25


    # Obtener los gastos adicionales de la receta
    gastos_adicionales = GastosAdicionalesReceta.objects.filter(receta=pedido)
    
    cant_gastos = GastosAdicionalesReceta.objects.filter(receta=pedido).count()

    if gastos_adicionales:
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x, y, f"COSTOS ADICIONALES:")
        y -= 20
        for gasto in gastos_adicionales:
            p.setFont("Helvetica", 10)  # Fuente en negrita
            p.drawString(x, y, f"{gasto.detalle}: $ {gasto.importe:,.2f}")
            y -= 20

    if cant_gastos <= 1:
        y = 725
    elif cant_gastos <= 3:
        y = 700
    else:
        y = 680
    
    y-=15

    insumos = ProductoReceta.objects.filter(receta=pedido)
    if insumos:
        p.setFont("Helvetica-Bold", 11)  # Fuente en negrita y tamaño 14
        p.drawString(x, y, f"ARTICULOS INCLUIDOS:")
        y -= 25
        for insumo in insumos:
            p.setFont("Helvetica-Bold", 9)
            if insumo.producto.descripcion:
                p.drawString(x, y, f"{str(insumo.producto.nombre).upper()} {str(insumo.producto.descripcion).upper()}")
            else:
                p.drawString(x, y, f"{str(insumo.producto.nombre).upper()}")
            y -= 15

            p.setFont("Helvetica", 10)
            p.drawString(x, y, f"Cant: {insumo.cantidad} {insumo.medida_uso} Subtotal : {moneda} {round(insumo.precio_unitario() or 0,2):,.2f}")
            y -= 20

    y = 725




    y = 60
    p.setFont("Helvetica-Bold", 14)
    p.drawString(280, y, "Precio total Presupuestado: ")
    p.setFont("Helvetica", 13)  # Fuente normal
    p.drawString(480, y,  f'$ {pedido.costo_receta():,.2f}')
    y -= 40

    p.save()

    return response
