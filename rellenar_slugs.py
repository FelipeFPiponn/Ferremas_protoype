from productos.models import Producto
from django.utils.text import slugify
from django.db import transaction

productos = Producto.objects.all()
with transaction.atomic():
    for p in productos:
        if not p.slug:
            base_slug = slugify(p.nombre)
            slug = base_slug
            i = 1
            while Producto.objects.filter(slug=slug).exclude(id=p.id).exists():
                slug = f'{base_slug}-{i}'
                i += 1
            p.slug = slug
            p.save()
print('Slugs actualizados correctamente.')
