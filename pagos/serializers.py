from rest_framework import serializers
from .models import Orden, Transaccion



class OrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden
        fields = '__all__'

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = ['id', 'token', 'monto', 'fecha', 'estado', 'codigo_autorizacion']
