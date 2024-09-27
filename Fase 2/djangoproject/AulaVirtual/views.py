from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import login as auth_login, authenticate, logout
from django.http import HttpResponse
from .forms import RegistroForm
from .models import Usuario
from .models import TipoUsuario

from .forms import CambiarPasswordForm
from .forms import RecuperarPasswordForm
from .forms import *
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, 'app/hijo.html')

@login_required
def perfil(request):
    usuario = request.user  # Obtener el usuario autenticado

    if request.method == 'POST':
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')

        # Validaciones básicas
        if not email:
            messages.error(request, 'El email es obligatorio.')
            return redirect('perfil')

        if not telefono:
            messages.error(request, 'El teléfono es obligatorio.')
            return redirect('perfil')

        # Validar formato básico de email
        if '@' not in email:
            messages.error(request, 'Por favor, ingrese un email válido.')
            return redirect('perfil')

        # Validar que el teléfono contenga solo números
        if not telefono.isdigit():
            messages.error(request, 'El teléfono debe contener solo números.')
            return redirect('perfil')

        # Actualizar los campos email y teléfono
        try:
            usuario.email = email
            usuario.telefono = telefono
            usuario.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al actualizar: {str(e)}')
            return redirect('perfil')

    # Renderizar la plantilla con los datos del usuario
    return render(request, 'app/perfil.html', {'usuario': usuario})

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

#Vista Administrador
def adminhome(request):
    return render(request, "app/administrador/adminhome.html")

def admincursos(request):
    return render(request, "app/administrador/admincursos.html")

def adminprofe(request):
    return render(request, "app/administrador/adminprofe.html")

def adminagregar(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.save()  # Guarda el usuario

            # Asigna automáticamente el rol "Alumno" al nuevo usuario
            tipo_usuario = TipoUsuario.objects.get(codigo=3)  # Suponiendo que el código 3 corresponde a "Alumno"
            usuario.tipo_usuario = tipo_usuario
            usuario.save()  # Guarda nuevamente el usuario con el tipo asignado

            messages.success(request, 'Usuario creado como Alumno correctamente!')
        else:
            messages.error(request, 'Hubo un error al crear el usuario.')

    return render(request, 'app/administrador/adminagregar.html', {'form': form})

def adminmodificar(request, id): 

    usuario = Usuario.objects.get(id=id)
    datos = {
        'form': UserForm(instance=usuario)
    }

    if request.method == 'POST':
        formulario = UserForm(request.POST, files=request.FILES, instance=usuario)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Usuario modificado correctamente!')
            datos['form'] = formulario

    return render(request, "app/administrador/adminmodificar.html", datos)
def adminusuario(request):
    usuarios = Usuario.objects.all()
    roles = TipoUsuario.objects.all()
    #Logica para cambiar el rol
    if request.method == 'POST':
        for usuario in usuarios:
            nuevo_rol_id = request.POST.get(f'rol_{usuario.id}')
            if nuevo_rol_id:
                nuevo_rol = TipoUsuario.objects.get(codigo=nuevo_rol_id)
                usuario.tipo_usuario = nuevo_rol
                usuario.save()  # Guarda el nuevo rol del usuario
                
        return redirect('adminusuario')
    
    return render(request, "app/administrador/adminusuario.html", {'usuarios': usuarios, 'roles': roles})

def eliminarUsuario(request, id):
    usuarios = Usuario.objects.get(id=id)
    usuarios.delete()
    return redirect(to="adminusuario")


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