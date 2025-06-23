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
from productos.models import Carrito
from .serializers import OrdenSerializer, TransaccionSerializer

# Importaciones actualizadas para Transbank SDK 6.0.0
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.error.transbank_error import TransbankError
from transbank.common.integration_type import IntegrationType
from transbank.webpay.transaccion_completa.transaction import Transaction


# Configuración de Transbank (Ambiente de integración)
def get_transbank_config():
    # Configuración para SDK 6.0.0 en ambiente de pruebas
    return WebpayOptions(
        commerce_code=Transaction.get_default_commerce_code(),
        api_key=Transaction.get_default_api_key(),
        integration_type=IntegrationType.TEST
    )

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
            return render(request, 'productos/checkout.html', {
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
            # Inicializar transacción con la nueva estructura
            tx = Transaction(options=get_transbank_config())
            
            buy_order = f'orden-{orden.id}'
            session_id = f'sesion-{request.user.id}'
            amount = int(orden.total)  # Transbank requiere un entero
            return_url = "https://072b-179-60-73-165.ngrok-free.app" + reverse('pago_retorno')
            
            print(f"Iniciando transacción: buy_order={buy_order}, session_id={session_id}, amount={amount}")
            print(f"URL de retorno: {return_url}")
            
            # Crear transacción con la nueva estructura
            response = tx.create(buy_order=buy_order, session_id=session_id, amount=amount, return_url=return_url)
            
            print(f"Respuesta de creación: {vars(response)}")
            
            # Guardar el token
            Transaccion.objects.create(
                orden=orden,
                token=response.token,
                monto=orden.total,
                estado='INICIADA'
            )
            
            # Usar la plantilla de redirección a Webpay
            return render(request, 'productos/confirmacion.html', {
                'url': response.url,
                'token': response.token
            })
            
        except TransbankError as e:
            print(f"Error de Transbank al crear transacción: {str(e)}")
            orden.estado = 'cancelado'
            orden.save()
            return render(request, 'productos/pago_fallido.html', {
                'error': f'Error al procesar el pago: {str(e)}'
            })
        except Exception as e:
            import traceback
            print(f"Error inesperado al crear transacción: {str(e)}")
            print(traceback.format_exc())
            orden.estado = 'cancelado'
            orden.save()
            return render(request, 'productos/pago_fallido.html', {
                'error': f'Error inesperado: {str(e)}'
            })
    
    return render(request, 'productos/checkout.html', {'carrito': carrito})

@csrf_exempt
def pago_retorno(request):
    # Depuración detallada
    print("\n" + "=" * 80)
    print("RETORNO DE PAGO - INFORMACIÓN COMPLETA")
    print("=" * 80)
    print(f"Método de la solicitud: {request.method}")
    print("\nTodos los parámetros POST:")
    for key, value in request.POST.items():
        print(f"  {key}: {value}")
    
    print("\nTodos los parámetros GET:")
    for key, value in request.GET.items():
        print(f"  {key}: {value}")
    
    # Verificar si es una respuesta de anulación o rechazo
    if 'TBK_TOKEN' in request.POST or 'TBK_TOKEN' in request.GET:
        print("\nDetectada respuesta con TBK_TOKEN - posible rechazo o anulación")
        tbk_token = request.POST.get('TBK_TOKEN') or request.GET.get('TBK_TOKEN')
        tbk_orden_compra = request.POST.get('TBK_ORDEN_COMPRA') or request.GET.get('TBK_ORDEN_COMPRA', '')
        
        print(f"TBK_TOKEN: {tbk_token}")
        print(f"TBK_ORDEN_COMPRA: {tbk_orden_compra}")
        
        # Intentar encontrar la transacción por el orden de compra
        if tbk_orden_compra and tbk_orden_compra.startswith('orden-'):
            try:
                orden_id = tbk_orden_compra.split('-')[1]
                print(f"Buscando orden con ID: {orden_id}")
                orden = get_object_or_404(Orden, id=orden_id)
                transaccion = orden.transaccion_set.first()
                
                if transaccion:
                    print(f"Transacción encontrada: {transaccion.id}, estado anterior: {transaccion.estado}")
                    transaccion.estado = 'RECHAZADA'
                    transaccion.save()
                    print(f"Estado actualizado a: RECHAZADA")
                
                return render(request, 'productos/pago_fallido.html', {
                    'error': 'Transacción rechazada o anulada por el usuario',
                    'detalles': f'TBK_TOKEN: {tbk_token}, TBK_ORDEN_COMPRA: {tbk_orden_compra}'
                })
            except Exception as e:
                import traceback
                print(f"Error al procesar TBK_TOKEN: {str(e)}")
                print(traceback.format_exc())
    
    # Continuar con el flujo normal para token_ws
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    
    print(f"\nToken obtenido: {token}")
    
    if not token:
        print("No se recibió token_ws")
        return render(request, 'productos/pago_fallido.html', {
            'error': 'No se recibió el token de la transacción',
            'detalles': 'Verifica los logs del servidor para más información'
        })
    
    try:
        # Buscar la transacción por el token
        print(f"Buscando transacción con token: {token}")
        transaccion = get_object_or_404(Transaccion, token=token)
        print(f"Transacción encontrada: ID={transaccion.id}, estado={transaccion.estado}, monto={transaccion.monto}")
        
        orden = transaccion.orden
        print(f"Orden asociada: ID={orden.id}, estado={orden.estado}, total={orden.total}")
        
        # Confirmar la transacción con Webpay
        print("\nConfirmando transacción con Webpay")
        tx = Transaction(options=get_transbank_config())
        
        try:
            print(f"Llamando a tx.commit con token: {token}")
            response = tx.commit(token=token)
            print(f"Respuesta recibida de Webpay")
            
            # Imprimir todos los atributos de la respuesta
            print("\nDetalles completos de la respuesta:")
            for attr_name in dir(response):
                if not attr_name.startswith('_'):  # Excluir atributos internos
                    try:
                        attr_value = getattr(response, attr_name)
                        if not callable(attr_value):  # Excluir métodos
                            print(f"  {attr_name}: {attr_value}")
                    except Exception as e:
                        print(f"  Error al obtener {attr_name}: {str(e)}")
            
            print(f"\nEstado de la respuesta: {response.status}")
            
            # Actualizar la transacción en nuestra base de datos
            transaccion.estado = response.status
            
            # Verificar si la transacción fue autorizada (más flexible)
            if response.status == 'AUTHORIZED' or 'AUTHORIZED' in response.status.upper():
                print("Transacción AUTORIZADA")
                transaccion.codigo_autorizacion = response.authorization_code
                orden.estado = 'pagado'
                orden.save()
                
                # Crear nuevo carrito
                Carrito.objects.create(usuario=orden.usuario)
                
                transaccion.save()
                
                # Redireccionar a la página de pago exitoso con la información de la orden y transacción
                return render(request, 'productos/pago_exito.html', {
                    'orden': orden,
                    'transaccion': transaccion,
                    'response': response
                })
            else:
                print(f"Transacción RECHAZADA: {response.status}")
                transaccion.save()
                return render(request, 'productos/pago_fallido.html', {
                    'error': f'Transacción rechazada por Webpay',
                    'detalles': f'Estado: {response.status}'
                })
                
        except TransbankError as e:
            print(f"Error de Transbank al confirmar: {str(e)}")
            return render(request, 'productos/pago_fallido.html', {
                'error': f'Error al confirmar el pago con Transbank',
                'detalles': str(e)
            })
            
    except TransbankError as e:
        print(f"Error de Transbank: {str(e)}")
        return render(request, 'productos/pago_fallido.html', {
            'error': f'Error al procesar el pago con Transbank',
            'detalles': str(e)
        })
    except Exception as e:
        import traceback
        print(f"Error inesperado: {str(e)}")
        print(traceback.format_exc())
        return render(request, 'productos/pago_fallido.html', {
            'error': f'Error inesperado durante el proceso de pago',
            'detalles': str(e)
        })

@login_required
def historial_ordenes(request):
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'productos/historial_ordenes.html', {'ordenes': ordenes})

@login_required
def detalle_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    return render(request, 'productos/detalle_orden.html', {'orden': orden})
