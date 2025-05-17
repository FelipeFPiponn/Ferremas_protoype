from django.core.management.base import BaseCommand
from productos.services import ProductoService

class Command(BaseCommand):
    help = 'Actualiza el catálogo de productos desde la API externa'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando actualización del catálogo...'))
        
        exito, mensaje = ProductoService.actualizar_catalogo_desde_api()
        
        if exito:
            self.stdout.write(self.style.SUCCESS(f'Actualización completada: {mensaje}'))
        else:
            self.stdout.write(self.style.ERROR(f'Error en la actualización: {mensaje}'))
