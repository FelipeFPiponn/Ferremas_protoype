import requests
from django.conf import settings
from .models import Producto, Categoria

class ProductoService:
    """
    Servicio para interactuar con la API de productos.
    Actúa como una capa de abstracción entre la API y las vistas.
    """
    
    @staticmethod
    def get_productos(filtros=None, pagina=1, items_por_pagina=12):
        """
        Obtiene productos desde la API con filtros opcionales.
        Por ahora, usa los modelos locales, pero está preparado para cambiarse a una API.
        """
        # Versión actual: usa modelos locales
        # Cuando tengas la API lista, reemplaza este código con llamadas a la API
        queryset = Producto.objects.filter(activo=True)
        
        if filtros:
            if 'categoria' in filtros:
                queryset = queryset.filter(categoria__slug=filtros['categoria'])
            if 'busqueda' in filtros:
                queryset = queryset.filter(nombre__icontains=filtros['busqueda'])
            if 'destacados' in filtros and filtros['destacados']:
                queryset = queryset.filter(destacado=True)
        
        # Ordenar productos
        queryset = queryset.order_by('-destacado', 'nombre')
        
        # Simulamos la paginación que vendría de la API
        total = queryset.count()
        inicio = (pagina - 1) * items_por_pagina
        fin = inicio + items_por_pagina
        productos = queryset[inicio:fin]
        
        # Estructura similar a lo que devolvería una API
        return {
            'productos': productos,
            'total': total,
            'pagina_actual': pagina,
            'total_paginas': (total + items_por_pagina - 1) // items_por_pagina
        }
    
    @staticmethod
    def get_producto_por_slug(slug):
        """
        Obtiene un producto específico por su slug.
        """
        # Versión actual: usa modelos locales
        try:
            return Producto.objects.get(slug=slug, activo=True)
        except Producto.DoesNotExist:
            return None
    
    @staticmethod
    def get_categorias():
        """
        Obtiene todas las categorías disponibles.
        """
        # Versión actual: usa modelos locales
        return Categoria.objects.all()
    
    @staticmethod
    def get_productos_relacionados(producto, limite=4):
        """
        Obtiene productos relacionados a un producto específico.
        """
        # Versión actual: usa modelos locales
        return Producto.objects.filter(
            categoria=producto.categoria, 
            activo=True
        ).exclude(id=producto.id)[:limite]
    
    @staticmethod
    def actualizar_catalogo_desde_api():
        """
        Método para actualizar el catálogo local desde la API externa.
        Este método se puede llamar manualmente o programar con Celery/cron.
        """
        # Aquí iría el código para consumir la API externa y actualizar la base de datos local
        # Por ejemplo:
        try:
            # URL de ejemplo, reemplaza con la URL real de tu API
            api_url = getattr(settings, 'API_PRODUCTOS_URL', 'https://api.example.com/productos')
            response = requests.get(api_url)
            
            if response.status_code == 200:
                productos_data = response.json()
                
                # Procesar cada producto de la API
                for producto_data in productos_data:
                    # Buscar o crear la categoría
                    categoria, _ = Categoria.objects.get_or_create(
                        nombre=producto_data['categoria'],
                        defaults={'slug': producto_data['categoria'].lower().replace(' ', '-')}
                    )
                    
                    # Buscar o crear el producto
                    Producto.objects.update_or_create(
                        codigo=producto_data['codigo'],
                        defaults={
                            'nombre': producto_data['nombre'],
                            'slug': producto_data.get('slug', producto_data['nombre'].lower().replace(' ', '-')),
                            'descripcion': producto_data.get('descripcion', ''),
                            'precio': producto_data['precio'],
                            'stock': producto_data.get('stock', 0),
                            'categoria': categoria,
                            'imagen': producto_data.get('imagen', ''),
                            'destacado': producto_data.get('destacado', False),
                            'activo': producto_data.get('activo', True)
                        }
                    )
                
                return True, f"Se actualizaron {len(productos_data)} productos"
            else:
                return False, f"Error al obtener datos de la API: {response.status_code}"
                
        except Exception as e:
            return False, f"Error al actualizar el catálogo: {str(e)}"
