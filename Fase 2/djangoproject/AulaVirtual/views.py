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
from .models import *
from .forms import CambiarPasswordForm
from .forms import RecuperarPasswordForm
from .forms import *
from django.contrib.auth.models import User
from django.utils import timezone #para el tiempo en vez de la bd 
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
def profesorcurso(request, rut_profesor):
    profesor = Usuario.objects.get(rut=rut_profesor, tipo_usuario__tipo='Profesor')
    cursos = Curso.objects.filter(profesor=profesor)

    context = {
        'profesor': profesor,
        'cursos': cursos
    }

    return render(request, "app/profesor/profesorcurso.html", context)

def profesorhome(request, id_curso):
    curso = Curso.objects.get(id=id_curso)
    profesor = request.user

    unidades = Unidad.objects.filter(curso=curso)

    context = {
        'curso': curso,
        'unidades': unidades,
        'profesor': profesor,  
        'es_profesor': request.user.tipo_usuario.tipo == 'Profesor'
    }
    return render(request, "app/profesor/profesorhome.html", context)

def profesoranotacion(request, id_alumno):
    alumno = Usuario.objects.get(id=id_alumno, tipo_usuario__tipo='Alumno')
    anotaciones = Anotacion.objects.filter(alumno=alumno)
    
    context = {
        'alumno': alumno,
        'anotaciones': anotaciones,
        
    }
    return render(request, "app/profesor/anotacion/profesoranotacion.html", context)


def profesorcrearanotacion(request, id_alumno, id_curso):
    alumno = Usuario.objects.get(id=id_alumno, tipo_usuario__tipo='Alumno')
    curso = Curso.objects.get(id=id_curso)
    profesor = request.user  

    if request.method == 'POST':
        form = AnotacionForm(request.POST)
        if form.is_valid():
            nueva_anotacion = form.save(commit=False)
            nueva_anotacion.alumno = alumno
            nueva_anotacion.profesor = profesor
            nueva_anotacion.curso = curso  
            nueva_anotacion.save()
            # Redirige correctamente con los argumentos esperados
            return redirect('profesoranotacionlista', rut_profesor=profesor.rut, id_curso=curso.id)
    else:
        form = AnotacionForm()

    context = {
        'alumno': alumno,
        'curso': curso,
        'form': form
    }

    return render(request, "app/profesor/anotacion/profesorcrearanotacion.html", context)


def profesobservaranotacion(request, id_alumno, id_curso):
    # Obtener el alumno y el curso
    alumno = Usuario.objects.get(id=id_alumno, tipo_usuario__tipo='Alumno')
    curso = Curso.objects.get(id=id_curso)
    
    # Obtener todas las anotaciones del alumno en el curso
    anotaciones = Anotacion.objects.filter(alumno=alumno, curso=curso).order_by('-fecha')

    context = {
        'alumno': alumno,
        'curso': curso,
        'anotaciones': anotaciones
    }

    return render(request, "app/profesor/anotacion/profesorobservaranotacion.html", context)



def profesoranuncio(request, id_curso):
    curso = Curso.objects.get(id=id_curso)  
    anuncio = Anuncio.objects.filter(curso=id_curso)  
    es_profesor = False


    if request.user.is_authenticated:
        usuario = Usuario.objects.get(id=request.user.id)
        if usuario.tipo_usuario.tipo == 'Profesor':
            es_profesor = True

    context = {
        'curso': curso,
        'anuncio': anuncio,
        'es_profesor': es_profesor
    }

    return render(request, 'app/profesor/anuncios/profesoranuncio.html', context)

def profesoragregaranuncio(request, id_curso):
    curso = Curso.objects.get(id=id_curso)
    profesor = request.user  
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.asignatura = curso.nombre
            anuncio.profesor = profesor
            anuncio.curso = curso  
            anuncio.fecha_creacion = timezone.now()
            anuncio.save()
            return redirect('profesoranuncio', id_curso=id_curso)
    else:
        form = AnuncioForm()

    context = {
        'curso': curso,
        'form': form,
        
    }

    return render(request, 'app/profesor/anuncios/profesoragregaranuncio.html', context )

def profesorasistencia(request):
    return render(request, "app/profesor/profesorasistencia.html")

def profesornotas(request):
    return render(request, "app/profesor/notas/profesornotas.html")

def profesoranotacionlista(request, rut_profesor, id_curso):
    profesor = Usuario.objects.get(rut=rut_profesor, tipo_usuario__tipo='Profesor')
    curso = Curso.objects.get(id=id_curso, profesor=profesor)

    # Obtener todos los alumnos del curso
    alumnos = Usuario.objects.filter(tipo_usuario__tipo='Alumno')

    context = {
        'profesor': profesor,
        'curso': curso,
        'alumnos': alumnos
    }

    return render(request, "app/profesor/anotacion/profesoranotacionlista.html", context)


def profesormaterial(request, id_curso):
    try:
        curso = Curso.objects.get(id=id_curso)
    except Curso.DoesNotExist:
        return redirect('pagina_error')

    unidades = Unidad.objects.filter(curso=curso)

    context = {
        'curso': curso,
        'unidades': unidades,
        'es_profesor': request.user.tipo_usuario.tipo == 'Profesor'  
    }

    return render(request, 'app/profesor/profesormaterial.html', context)


def agregar_contenido(request, unidad_id):
    unidad = Unidad.objects.get(id=unidad_id)
    
    if request.method == 'POST':
        form = RecursoForm(request.POST, request.FILES)
        if form.is_valid():
            recurso = form.save(commit=False)
            recurso.unidad = unidad  # Asignar la unidad al recurso
            recurso.save()
            return redirect('profesormaterial', id_curso=unidad.curso.id)
    else:
        form = RecursoForm()

    return render(request, 'app/profesor/agregarcontenido.html', {'form': form, 'unidad': unidad})


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