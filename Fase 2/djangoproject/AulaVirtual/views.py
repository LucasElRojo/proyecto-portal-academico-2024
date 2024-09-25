from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import login as auth_login, authenticate, logout
from .models import Usuario
from django.http import HttpResponse
from .forms import RegistroForm
from .models import Usuario
import firebase_admin
from firebase_admin import auth
from .forms import CambiarPasswordForm
from .forms import RecuperarPasswordForm

# Create your views here.
def index(request):
    return render(request, 'app/hijo.html')

def perfil(request):
    return render(request, 'app/perfil.html')

def anotaciones(request):
    return render(request, 'app/anotaciones.html')

def anuncios(request):
    return render(request, 'app/anuncios.html')

def hijo(request):
    return render(request, 'app/hijo.html')

def asistencia(request):
    return render(request, "app/asistencia.html")

def horario(request):
    return render(request, "app/horario.html")

def notas(request):
    return render(request, "app/notas.html")

def calendario(request):
    return render(request, "app/calendario.html")

# Vistas Profesor
def profesorcurso(request):
    return render(request, "app/profesor/profesorcurso.html")

def profesorhome(request):
    return render(request, "app/profesor/profesorhome.html")

def profesorasistencia(request):
    return render(request, "app/profesor/profesorasistencia.html")

def profesornotas(request):
    return render(request, "app/profesor/profesornotas.html")

def profesoranotacionlista(request):
    return render(request, "app/profesor/profesoranotacionlista.html")

def profesoranuncio(request):
    return render(request, "app/profesor/profesoranuncio.html")

def profesormaterial(request):
    return render(request, "app/profesor/profesormaterial.html")

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            rut = form.cleaned_data.get('rut')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(rut=rut, password=raw_password)
            if user:
                login(request, user)  # Esta es la forma correcta de usar login
                messages.success(request, '¡Registro exitoso!')
                return redirect('index')  # Redirigir a la página de inicio
    else:
        form = RegistroForm()

    return render(request, 'app/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data.get('rut')
            password = form.cleaned_data.get('password')
            user = authenticate(request, rut=rut, password=password)
            if user:
                login(request, user)
                return redirect('perfil')  # Redirigir a la pagina de perfil
    else:
        form = LoginForm()

    return render(request, 'app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')  # Redirigir a la página de inicio después de cerrar sesión


@login_required
def cambiar_password_view(request):
    if request.method == 'POST':
        form = CambiarPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            nueva_password = form.cleaned_data.get('nueva_password')
            request.user.set_password(nueva_password)
            request.user.save()
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('index')  # Redirige al index
    else:
        form = CambiarPasswordForm(user=request.user)

    return render(request, 'app/cambiar_password.html', {'form': form})

def recuperar_password_view(request):
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data.get('rut')
            nueva_password = form.cleaned_data.get('nueva_password')
            try:
                usuario = Usuario.objects.get(rut=rut)
                usuario.set_password(nueva_password)
                usuario.save()
                messages.success(request, 'Contraseña restablecida exitosamente.')
                return redirect('login')  # Redirige al login después de cambiar la contraseña
            except Usuario.DoesNotExist:
                form.add_error('rut', 'El RUT ingresado no existe.')
    else:
        form = RecuperarPasswordForm()

    return render(request, 'app/recuperar_password.html', {'form': form})