from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import Orden, Transaccion
from carrito.models import Carrito
from .serializers import OrdenSerializer, TransaccionSerializer

# Importamos la librería de Transbank
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import IntegrationCommerceCodes, IntegrationApiKeys, Environment

# Configuración de Transbank (Ambiente de integración)
def get_transbank_config():
    # Para ambiente de integración
    return {
        'commerce_code': IntegrationCommerceCodes.WEBPAY_PLUS,
        'api_key': IntegrationApiKeys.WEBPAY_PLUS,
        'environment': Environment.INTEGRATION
    }

# API Views
class OrdenViewSet(viewsets.ModelViewSet):
    serializer_class = OrdenSerializer
    
    def get_queryset(self):
        return Orden.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['post'])
    def crear_orden(self, request):
        # Obtener el carrito del usuario
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            if not carrito.items.exists():
                return Response({"error": "El carrito está vacío"}, status=status.HTTP_400_BAD_REQUEST)
        except Carrito.DoesNotExist:
            return Response({"error": "No se encontró un carrito para este usuario"}, status=status.HTTP_404_NOT_FOUND)
        
        # Crear la orden
        direccion = request.data.get('direccion', '')
        if not direccion:
            return Response({"error": "Se requiere una dirección de envío"}, status=status.HTTP_400_BAD_REQUEST)
        
        orden = Orden.objects.create(
            usuario=request.user,
            carrito=carrito,
            direccion_envio=direccion,
            total=carrito.total
        )
        
        serializer = OrdenSerializer(orden)
        return Response(serializer.data)

# Template Views
@login_required
def checkout(request):
    # Obtener el carrito del usuario
    try:
        carrito = Carrito.objects.get(usuario=request.user)
        if not carrito.items.exists():
            return redirect('ver_carrito')
    except Carrito.DoesNotExist:
        return redirect('ver_carrito')
    
    if request.method == 'POST':
        direccion = request.POST.get('direccion', '')
        if not direccion:
            return render(request, 'pagos/checkout.html', {
                'carrito': carrito,
                'error': 'Se requiere una dirección de envío'
            })
        
        # Crear la orden
        orden = Orden.objects.create(
            usuario=request.user,
            carrito=carrito,
            direccion_envio=direccion,
            total=carrito.total
        )
        
        # Iniciar transacción con Transbank
        try:
            tx = Transaction(**get_transbank_config())
            
            buy_order = f'orden-{orden.id}'
            session_id = f'sesion-{request.user.id}'
            amount = int(orden.total)  # Transbank requiere un entero
            return_url = request.build_absolute_uri(reverse('pago_retorno'))
            
            response = tx.create(buy_order, session_id, amount, return_url)
            
            # Guardar el token
            Transaccion.objects.create(
                orden=orden,
                token=response.token,
                monto=orden.total,
                estado='INICIADA'
            )
            
            # Redireccionar al usuario a la página de pago de Webpay
            return redirect(response.url + '?token_ws=' + response.token)
            
        except TransbankError as e:
            orden.estado = 'cancelado'
            orden.save()
            return render(request, 'pagos/error.html', {
                'error': f'Error al procesar el pago: {str(e)}'
            })
    
    return render(request, 'pagos/checkout.html', {'carrito': carrito})

@csrf_exempt
def pago_retorno(request):
    token = request.POST.get('token_ws')
    
    if not token:
        return render(request, 'pagos/error.html', {
            'error': 'No se recibió el token de la transacción'
        })
    
    try:
        # Buscar la transacción por el token
        transaccion = get_object_or_404(Transaccion, token=token)
        orden = transaccion.orden
        
        # Confirmar la transacción con Webpay
        tx = Transaction(**get_transbank_config())
        response = tx.commit(token)
        
        # Actualizar la transacción en nuestra base de datos
        transaccion.estado = response.status
        
        if response.status == 'AUTHORIZED':
            transaccion.codigo_autorizacion = response.authorization_code
            orden.estado = 'pagado'
            orden.save()
            
            # Aquí podrías crear un nuevo carrito para el usuario
            # y dejar el anterior asociado a la orden
            Carrito.objects.create(usuario=orden.usuario)
            
            transaccion.save()
            return render(request, 'pagos/confirmacion.html', {
                'orden': orden,
                'transaccion': transaccion,
                'response': response
            })
        else:
            transaccion.save()
            return render(request, 'pagos/error.html', {
                'error': f'Transacción rechazada: {response.status}'
            })
            
    except TransbankError as e:
        return render(request, 'pagos/error.html', {
            'error': f'Error al confirmar el pago: {str(e)}'
        })
    except Exception as e:
        return render(request, 'pagos/error.html', {
            'error': f'Error inesperado: {str(e)}'
        })

@login_required
def historial_ordenes(request):
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'pagos/historial_ordenes.html', {'ordenes': ordenes})

@login_required
def detalle_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    return render(request, 'pagos/detalle_orden.html', {'orden': orden})
