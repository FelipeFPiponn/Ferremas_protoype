from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from productos.models import Producto, Categoria, Carrito
from django.db import models

def get_cart_count(request):
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            return carrito.items.aggregate(total=models.Sum('cantidad'))['total'] or 0
        except Carrito.DoesNotExist:
            return 0
    return 0

def home(request):
    productos_destacados = Producto.objects.filter(destacado=True)
    if not productos_destacados.exists():
        productos_destacados = Producto.objects.all()[:6]  # Mostrar hasta 6 productos si no hay destacados
    categorias = Categoria.objects.all()
    cart_count = get_cart_count(request)
    return render(request, 'home.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'cart_count': cart_count
    })


# catálogo
def catalogo(request):
    # Obtener todos los productos
    productos = Producto.objects.all()
    
    # Filtrar por categoría si se proporciona
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    # Filtrar por subcategoría si se proporciona
    subcategoria = request.GET.get('subcategoria')
    if subcategoria:
        # Asumiendo que tienes un campo subcategoria o similar en tu modelo Producto
        # Usamos icontains para una búsqueda más flexible
        productos = productos.filter(
            models.Q(subcategoria__icontains=subcategoria) | 
            models.Q(nombre__icontains=subcategoria) |
            models.Q(descripcion__icontains=subcategoria)
        )
    
    # Filtrar por precio mínimo si se proporciona
    precio_min = request.GET.get('precio_min')
    if precio_min and precio_min.isdigit():
        productos = productos.filter(precio__gte=float(precio_min))
    
    # Filtrar por precio máximo si se proporciona
    precio_max = request.GET.get('precio_max')
    if precio_max and precio_max.isdigit():
        productos = productos.filter(precio__lte=float(precio_max))
    
    
    # Obtener categorías para el menú lateral
    categorias = Categoria.objects.all()
    
    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
    })

# Vista para las ofertas
def ofertas(request):
    # Aquí podrías obtener productos en oferta
    ofertas = []  # Reemplazar con consulta a la base de datos
    return render(request, 'tienda/ofertas.html', {'ofertas': ofertas})

# Vista para la página de contacto
def contacto(request):
    if request.method == 'POST':
        # Procesar formulario de contacto
        messages.success(request, "Tu mensaje ha sido enviado correctamente. Nos pondremos en contacto contigo pronto.")
        return redirect('contacto')
    return render(request, 'tienda/contacto.html')

# Vista para la página "Nosotros"
def nosotros(request):
    return render(request, 'tienda/nosotros.html')

# Vista para los términos y condiciones
def terminos(request):
    return render(request, 'tienda/terminos.html')

# Vista para iniciar sesión
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'tienda/login.html', {'form': form})

# Vista para registrarse
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso! Bienvenido a Ferreemas.")
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'tienda/registro.html', {'form': form})

# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('home')

# Vista para el perfil de usuario (requiere inicio de sesión)
@login_required
def perfil(request):
    return render(request, 'tienda/perfil.html')

# Vista para los pedidos del usuario (requiere inicio de sesión)
@login_required
def pedidos(request):
    # Aquí podrías obtener los pedidos del usuario actual
    pedidos = []  # Reemplazar con consulta a la base de datos
    return render(request, 'tienda/pedidos.html', {'pedidos': pedidos})

# Vista para el carrito de compras
def carrito(request):
    # Aquí podrías obtener los productos en el carrito del usuario
    productos_carrito = []  # Reemplazar con lógica de carrito
    return render(request, 'tienda/ver_carrito.html', {'productos': productos_carrito})