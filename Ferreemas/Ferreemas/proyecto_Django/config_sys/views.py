from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm



def home(request):
    return render(request, 'base.html')


# catálogo
def catalogo(request):
    # Aquí podrías obtener productos de la base de datos
    productos = []  # Reemplazar con consulta a la base de datos
    return render(request, 'tienda/catalogo.html', {'productos': productos})

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