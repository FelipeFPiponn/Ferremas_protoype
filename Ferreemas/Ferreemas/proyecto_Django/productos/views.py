from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .services import ProductoService

def lista_productos(request):
    """Vista para mostrar el catálogo de productos"""
    pagina = int(request.GET.get('page', 1))
    
    # Usar el servicio para obtener los productos
    resultado = ProductoService.get_productos(pagina=pagina)
    
    # Obtener categorías para el menú lateral
    categorias = ProductoService.get_categorias()
    
    return render(request, 'productos/lista.html', {
        'productos': resultado['productos'],
        'total': resultado['total'],
        'pagina_actual': resultado['pagina_actual'],
        'total_paginas': resultado['total_paginas'],
        'categorias': categorias
    })

def detalle_producto(request, slug):
    """Vista para mostrar el detalle de un producto"""
    # Usar el servicio para obtener el producto
    producto = ProductoService.get_producto_por_slug(slug)
    
    if not producto:
        messages.error(request, 'El producto solicitado no existe o no está disponible.')
        return redirect('lista_productos')
    
    # Obtener productos relacionados
    productos_relacionados = ProductoService.get_productos_relacionados(producto)
    
    return render(request, 'productos/detalle.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados
    })

def productos_por_categoria(request, slug):
    """Vista para mostrar productos por categoría"""
    pagina = int(request.GET.get('page', 1))
    
    # Usar el servicio para obtener los productos filtrados por categoría
    resultado = ProductoService.get_productos(
        filtros={'categoria': slug},
        pagina=pagina
    )
    
    # Obtener categorías para el menú lateral
    categorias = ProductoService.get_categorias()
    
    # Obtener la categoría actual
    categoria_actual = next((c for c in categorias if c.slug == slug), None)
    
    return render(request, 'productos/categoria.html', {
        'categoria': categoria_actual,
        'productos': resultado['productos'],
        'total': resultado['total'],
        'pagina_actual': resultado['pagina_actual'],
        'total_paginas': resultado['total_paginas'],
        'categorias': categorias
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
    
    return render(request, 'productos/busqueda.html', {
        'query': query,
        'productos': resultado['productos'],
        'total': resultado['total'],
        'pagina_actual': resultado['pagina_actual'],
        'total_paginas': resultado['total_paginas'],
        'categorias': categorias
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
