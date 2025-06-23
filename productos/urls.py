from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('categoria/<int:pk>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('actualizar-catalogo/', views.actualizar_catalogo, name='actualizar_catalogo'),
    path('<int:pk>/', views.detalle_producto, name='detalle_producto'),
    # Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/checkout/', views.iniciar_pago, name='iniciar_pago'),
    path('carrito/crear-transaccion/', views.crear_transaccion, name='crear_transaccion'),
    path('carrito/retorno/', views.retorno_webpay, name='retorno_webpay'),
]

