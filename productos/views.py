from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .services import ProductoService
from .models import Producto, Categoria, Carrito, ItemCarrito
from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from django.conf import settings
from django.db import models

def get_cart_count(request):
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            return carrito.items.aggregate(total=models.Sum('cantidad'))['total'] or 0
        except Carrito.DoesNotExist:
            return 0
    return 0

def lista_productos(request):
    """Vista para mostrar el catálogo de productos"""
    pagina = int(request.GET.get('page', 1))
    
    # Usar el servicio para obtener los productos
    resultado = ProductoService.get_productos(pagina=pagina)
    
    # Obtener categorías para el menú lateral
    categorias = ProductoService.get_categorias()
    cart_count = get_cart_count(request)
    return render(request, 'productos/lista.html', {
        'productos': resultado['productos'],
        'total': resultado['total'],
        'pagina_actual': resultado['pagina_actual'],
        'total_paginas': resultado['total_paginas'],
        'categorias': categorias,
        'cart_count': cart_count
    })

def detalle_producto(request, pk):
    """Vista para mostrar el detalle de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    productos_relacionados = Producto.objects.filter(categoria=producto.categoria).exclude(id=producto.id)[:4]
    cart_count = get_cart_count(request)
    return render(request, 'productos/detalle.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'cart_count': cart_count
    })

def productos_por_categoria(request, pk):
    """Vista para mostrar productos por categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    productos = Producto.objects.filter(categoria=categoria)
    categorias = Categoria.objects.all()
    cart_count = get_cart_count(request)
    return render(request, 'productos/categoria.html', {
        'categoria': categoria,
        'productos': productos,
        'categorias': categorias,
        'cart_count': cart_count
    })

def buscar_productos(request):
    """Vista para buscar productos"""
    query = request.GET.get('q', '')
    pagina = int(request.GET.get('page', 1))
    
    if query:
        # Usar el servicio para buscar productos
        resultado = ProductoService.get_productos(
            filtros={'busqueda': query},
            pagina=pagina
        )
    else:
        resultado = {
            'productos': [],
            'total': 0,
            'pagina_actual': 1,
            'total_paginas': 0
        }
    
    # Obtener categorías para el menú lateral
    categorias = ProductoService.get_categorias()
    cart_count = get_cart_count(request)
    return render(request, 'productos/busqueda.html', {
        'query': query,
        'productos': resultado['productos'],
        'total': resultado['total'],
        'pagina_actual': resultado['pagina_actual'],
        'total_paginas': resultado['total_paginas'],
        'categorias': categorias,
        'cart_count': cart_count
    })

def actualizar_catalogo(request):
    """
    Vista para actualizar manualmente el catálogo desde la API.
    Solo accesible para administradores.
    """
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('home')
    
    exito, mensaje = ProductoService.actualizar_catalogo_desde_api()
    
    if exito:
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)
    
    return redirect('lista_productos')

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    if not created:
        item.cantidad += 1
        item.save()
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    user = request.user
    if user.is_authenticated:
        carrito = getattr(user, 'carrito', None)
        if carrito:
            items = [item for item in carrito.items.all() if hasattr(item, 'producto') and item.producto is not None]
            total = carrito.total() if hasattr(carrito, 'total') else sum(item.subtotal() for item in items)
        else:
            items = []
            total = 0
    else:
        items = []
        total = 0
    return render(request, 'productos/ver_carrito.html', {
        'items': items,
        'total': total,
        'cart_count': len(items)
    })

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')

@login_required
def actualizar_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        item.cantidad = max(1, cantidad)
        item.save()
    return redirect('ver_carrito')

@login_required
def iniciar_pago(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto')
    total = carrito.total() if hasattr(carrito, 'total') else sum(item.subtotal() for item in items)
    cart_count = get_cart_count(request)
    return render(request, 'productos/checkout.html', {'carrito': carrito, 'items': items, 'total': total, 'cart_count': cart_count})

@login_required
def crear_transaccion(request):
    if request.method != 'POST':
        return redirect('iniciar_pago')
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto')
    total = carrito.total() if hasattr(carrito, 'total') else sum(item.subtotal() for item in items)
    if not items:
        return redirect('ver_carrito')
    # Configuración de Transbank Webpay Plus (modo integración)
    tx = Transaction.build_for_integration(
        IntegrationCommerceCodes.WEBPAY_PLUS,
        IntegrationApiKeys.WEBPAY
    )
    buy_order = f"ORD-{request.user.id}-{carrito.id}-{int(carrito.actualizado.timestamp())}"
    session_id = str(request.user.id)
    amount = int(total)
    return_url = request.build_absolute_uri('/productos/carrito/retorno/')
    response = tx.create(buy_order, session_id, amount, return_url)
    url = response['url']
    token = response['token']
    return render(request, 'productos/redirigir_webpay.html', {'url': url, 'token': token})

@csrf_exempt
def retorno_webpay(request):
    token = request.POST.get('token_ws')
    if not token:
        return render(request, 'productos/pago_fallido.html')
    tx = Transaction.build_for_integration(
        IntegrationCommerceCodes.WEBPAY_PLUS,
        IntegrationApiKeys.WEBPAY
    )
    response = tx.commit(token)
    if response['status'] == 'AUTHORIZED':
        # Aquí puedes marcar el carrito/pedido como pagado
        return render(request, 'productos/pago_exito.html', {'response': response})
    else:
        return render(request, 'productos/pago_fallido.html', {'response': response})


