from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('categoria/<slug:slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('actualizar-catalogo/', views.actualizar_catalogo, name='actualizar_catalogo'),
    path('<slug:slug>/', views.detalle_producto, name='detalle_producto'),
]
