from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import login as auth_login, authenticate, logout
from django.http import HttpResponse, HttpResponseBadRequest
from .forms import RegistroForm
from .models import Usuario
from .models import TipoUsuario
from .models import *
from .forms import CambiarPasswordForm
from .forms import RecuperarPasswordForm
from .forms import *
from django.utils import timezone #para el tiempo 
from datetime import datetime
from django.views.generic import ListView, FormView
from django.views.generic import ListView,FormView
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your views here.
def index(request):
    return render(request, 'app/hijo.html')

class BasicEmailView(FormView, ListView):    
    template_name = "app/emailhome.html"
    context_object_name = 'mydata'
    model = Emails
    form_class = EmailForm
    success_url = "/"

    def form_valid(self, form):
        my_subject = "¡Tus Notas Mensuales Han Llegado!"
        my_recipient = form.cleaned_data['email']

        if Usuario.objects.filter(email=my_recipient).exists():
            user = Usuario.objects.get(email=my_recipient)
            welcome_message = f"Hola {user.primer_nombre} {user.primer_apellido}, ¡aquí están tus notas más recientes!"

            notas_por_curso = obtener_notas_usuario(user)
        else: 
            welcome_message = "¡Hola! Revisa tus notas del mes."
            user = None
            notas_por_curso = {}

        link_app = "http://localhost:8000"

        context = {
            "welcome_message": welcome_message, 
            "link_app": link_app,
            "user": user,
            "notas_por_curso": notas_por_curso
        }
                
        html_message = render_to_string("app/email.html", context=context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject=my_subject, 
            body=plain_message,
            from_email=None,
            to=[my_recipient]
        )

        message.attach_alternative(html_message, "text/html")
        message.send()

        # Guardamos el email enviado en la base de datos
        Emails.objects.create(
            subject=my_subject, 
            message="Hemos enviado este correo", 
            email=my_recipient
        )
        
        return super().form_valid(form)


def obtener_notas_usuario(user):
    # Obtenemos todas las notas del alumno
    notas = Nota.objects.filter(alumno=user).select_related('curso').order_by('curso__nombre', 'numero_nota')
    
    # Diccionario para almacenar las notas por curso
    notas_por_curso = {}
    for nota in notas:
        curso = nota.curso
        if curso not in notas_por_curso:
            notas_por_curso[curso] = []
        notas_por_curso[curso].append(nota)
    
    # Asegurarse de que siempre haya 5 notas por curso (rellenar con None si faltan)
    for notas_list in notas_por_curso.values():
        while len(notas_list) < 5:
            notas_list.append(None)
    
    return notas_por_curso



def alumnonotas(request, rut_alumno):
    alumno = Usuario.objects.get(rut=rut_alumno, tipo_usuario__tipo='Alumno')
    cursos = alumno.cursos.all()

    # Diccionario para almacenar las notas por curso
    notas_por_curso = {}
    for curso in cursos:
        notas = list(Nota.objects.filter(alumno=alumno, curso=curso).order_by('numero_nota'))
        
        # Asegurarse de que siempre haya 5 notas (rellenar con None si faltan)
        while len(notas) < 5:
            notas.append(None)
        
        notas_por_curso[curso] = notas

    context = {
        'alumno': alumno,
        'notas_por_curso': notas_por_curso,
        'rango_notas': range(1, 6),  # Se ajusta segun las notas 
    }

    return render(request, 'app/alumno/notas/alumnonotas.html', context)

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
    # Obtenemos el primer nombre y apellido del usuario actual
    user_first_name = request.user.primer_nombre
    user_first_surname = request.user.primer_apellido

    # Filtramos los cursos donde el alumno tiene asistencias
    cursos = Curso.objects.filter(
        clases__asistencias__alumno__primer_nombre=user_first_name,
        clases__asistencias__alumno__primer_apellido=user_first_surname
    ).distinct().prefetch_related('clases__asistencias')
    return render(request, "app/asistencia.html", {'cursos': cursos})

def crear_clase_y_tomar_asistencia(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    clase = None  # Inicialmente no hay clase
    
    # Cambia esta línea para asegurar que traes a los alumnos correctos
    alumnos = Usuario.objects.filter(tipo_usuario__tipo='Alumno')
    
    clases = Clase.objects.filter(curso=curso).order_by('-fecha')
    
    clases_con_asistencia = []
    for c in clases:
        total_alumnos = alumnos.count()
        total_asistencias = Asistencia.objects.filter(clase=c).count()
        total_presentes = Asistencia.objects.filter(clase=c, estado='S').count()
        total_ausentes = Asistencia.objects.filter(clase=c, estado='N').count()
        total_justificados = Asistencia.objects.filter(clase=c, estado='J').count()
        clases_con_asistencia.append({
            'clase': c,
            'total_alumnos': total_alumnos,
            'total_asistencias': total_asistencias,
            'total_presentes': total_presentes,
            'total_ausentes': total_ausentes,
            'total_justificados': total_justificados,
        })
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'crear_clase':
            clase_form = ClaseForm(request.POST)
            if clase_form.is_valid():
                clase = clase_form.save(commit=False)
                clase.curso = curso
                clase.save()
                asistencia_form = AsistenciaForm(alumnos=alumnos)
                return render(request, 'app/tomarasistencia.html', {
                    'clase_form': clase_form,
                    'asistencia_form': asistencia_form,
                    'clase': clase,
                    'curso': curso,
                    'clases_con_asistencia': clases_con_asistencia,
                })
        elif action == 'tomar_asistencia':
            clase_id = request.POST.get('clase_id')
            clase = get_object_or_404(Clase, id=clase_id)
            asistencia_form = AsistenciaForm(request.POST, alumnos=alumnos)
            if asistencia_form.is_valid():
                for alumno in alumnos:
                    estado = asistencia_form.cleaned_data.get(f'estado_{alumno.id}')
                    Asistencia.objects.update_or_create(
                        clase=clase,
                        alumno=alumno,
                        defaults={'estado': estado}
                    )
                # Actualizar la lista de clases
                clases = Clase.objects.filter(curso=curso).order_by('-fecha')
                clases_con_asistencia = []
                for c in clases:
                    total_alumnos = alumnos.count()
                    total_asistencias = Asistencia.objects.filter(clase=c).count()
                    total_presentes = Asistencia.objects.filter(clase=c, estado='S').count()
                    total_ausentes = Asistencia.objects.filter(clase=c, estado='N').count()
                    total_justificados = Asistencia.objects.filter(clase=c, estado='J').count()
                    clases_con_asistencia.append({
                        'clase': c,
                        'total_alumnos': total_alumnos,
                        'total_asistencias': total_asistencias,
                        'total_presentes': total_presentes,
                        'total_ausentes': total_ausentes,
                        'total_justificados': total_justificados,
                    })
                initial_data = {'fecha': datetime.today().strftime('%Y-%m-%d')}
                clase_form = ClaseForm(initial=initial_data)
                return render(request, 'app/tomarasistencia.html', {
                    'clase_form': clase_form,
                    'curso': curso,
                    'clases_con_asistencia': clases_con_asistencia,
                    'message': 'Asistencia guardada correctamente',
                })
    else:
        initial_data = {'fecha': datetime.today().strftime('%Y-%m-%d')}
        clase_form = ClaseForm(initial=initial_data)
        return render(request, 'app/tomarasistencia.html', {
            'clase_form': clase_form,
            'curso': curso,
            'clases_con_asistencia': clases_con_asistencia,
        })


def horario(request):
    return render(request, "app/horario.html")

def notas(request):
    return render(request, "app/notas.html")

def calendario(request):
    return render(request, "app/calendario.html")

# Vistas Alumno


def detalle_clase(request, id_curso):
    clase = get_object_or_404(Clase, id=id_curso)
    curso = clase.curso
    asistencias = Asistencia.objects.filter(clase=clase)
    return render(request, 'app/detalle_clase.html', {'clase': clase, 'asistencias': asistencias})

def alumnocurso(request, rut_alumno):
    alumno = Usuario.objects.get(rut=rut_alumno, tipo_usuario__tipo='Alumno')
    cursos = Curso.objects.filter(alumnos = alumno)

    context ={
        'alumno' : alumno,
        'cursos' : cursos,

    }

    return render(request, 'app/alumno/alumnocurso.html', context)


def alumnohome(request, id_curso):
    curso = Curso.objects.get(id=id_curso)
    alumno = request.user

    unidades = Unidad.objects.filter(curso=curso)

    context = {
        'curso': curso,
        'unidades': unidades,
        'alumno': alumno,  
        'es_profesor': request.user.tipo_usuario.tipo == 'Profesor'
    }

    return render(request, 'app/alumno/alumnohome.html', context)



def alumnoanotacion(request, rut_alumno):
    alumno = Usuario.objects.get(rut=rut_alumno, tipo_usuario__tipo='Alumno')
    anotaciones = Anotacion.objects.filter(alumno=alumno).select_related('curso', 'profesor')

    context = {
        'alumno': alumno,
        'anotaciones': anotaciones
    }

    return render(request, "app/alumno/anotacion/alumnoanotacion.html", context)



def alumnoanuncio(request, rut_alumno):
    alumno = Usuario.objects.get(rut=rut_alumno, tipo_usuario__tipo='Alumno')
    cursos = alumno.cursos.all()

    anuncios = Anuncio.objects.filter(curso__in=cursos).order_by('-fecha')

    context = {
        'alumno': alumno,
        'anuncios': anuncios,
    }

    return render(request, 'app/alumno/anuncios/alumnoanuncio.html', context)

def alumnomaterial(request, rut_alumno, id_curso):
    alumno = Usuario.objects.get(rut=rut_alumno, tipo_usuario__tipo='Alumno')
    curso = Curso.objects.get(id=id_curso, alumnos=alumno)

    unidades = Unidad.objects.filter(curso=curso).prefetch_related('recurso_set')

    context = {
        'alumno': alumno,
        'curso': curso,
        'unidades': unidades,
    }

    return render(request, 'app/alumno/material/alumnomaterial.html', context)




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
    alumnos = Usuario.objects.filter(cursos=curso, tipo_usuario__tipo='Alumno')


    
    context = {
        'curso': curso,
        'unidades': unidades,
        'alumnos': alumnos,
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

def profesornotas(request, id_curso):
    curso = Curso.objects.get(id=id_curso)
    
    # Obtener todos los alumnos inscritos en el curso
    alumnos = Usuario.objects.filter(tipo_usuario__tipo='Alumno')

    # Crear un diccionario que asocie cada alumno con sus notas
    alumnos_con_notas = {}
    for alumno in alumnos:
        # Ordenar las notas por su número (si tienes un campo para el número de la nota)
        notas = Nota.objects.filter(alumno=alumno, curso=curso).order_by('numero_nota')
        alumnos_con_notas[alumno] = notas

    context = {
        'curso': curso,
        'alumnos_con_notas': alumnos_con_notas,
    }

    return render(request, 'app/profesor/notas/profesornotas.html', context)




def agregarnota(request, id_curso):
    curso = Curso.objects.get(id=id_curso)
    alumnos = Usuario.objects.filter(tipo_usuario__tipo='Alumno')
    numero_minimo_notas = 5  # El número mínimo de notas

    if request.method == 'POST':
        for alumno in alumnos:
            for numero_nota in range(1, numero_minimo_notas + 1):
                valor_nota = request.POST.get(f'nota{numero_nota}_{alumno.id}')
                if valor_nota:
                    # Usar update_or_create para actualizar la nota si ya existe
                    Nota.objects.update_or_create(
                        alumno=alumno, curso=curso, numero_nota=numero_nota,
                        defaults={'valor': valor_nota}  # Valores a actualizar
                    )

        messages.success(request, 'Notas guardadas exitosamente.')
        return redirect('agregarnota', id_curso=curso.id)

    # Diccionario para contener las notas de cada alumno
    alumnos_con_notas = {}
    for alumno in alumnos:
        notas = Nota.objects.filter(alumno=alumno, curso=curso).order_by('numero_nota')
        alumnos_con_notas[alumno] = notas

    context = {
        'curso': curso,
        'alumnos_con_notas': alumnos_con_notas,
        'rango_notas': range(1, numero_minimo_notas + 1),
    }

    return render(request, 'app/profesor/notas/agregarnota.html', context)


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

def admincursoshome(request):
    
    return render(request, "app/administrador/cursos/admincursoshome.html")

def adminprofe(request):
    return render(request, "app/administrador/adminprofe.html")

def adminagregar(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)  
            raw_password = form.cleaned_data.get('password')   #Aqui se encripta la contraseña
            usuario.set_password(raw_password)  
            usuario.save()  


            tipo_usuario = TipoUsuario.objects.get(codigo=3)  #Aqui se asigna automaticamente que el usuario creado sea alumno
            usuario.tipo_usuario = tipo_usuario
            usuario.save()  

            messages.success(request, 'Usuario creado como Alumno correctamente!')
            return redirect('adminusuario')
        else:
            messages.error(request, 'Hubo un error al crear el usuario.')

    return render(request, 'app/administrador/usuarios/manejo_usuario/adminagregar.html', {'form': form})


def adminmodificar(request, id):
    usuario = Usuario.objects.get(id=id)
    form = UserForm(instance=usuario)  

    if request.method == 'POST':
        form = UserForm(request.POST, instance=usuario)  
        
        if form.is_valid():
            # Comprobar si se cambió la contraseña
            new_password = form.cleaned_data.get('password')
            
            # encripta la contraseña antes de guardar
            if new_password:
                usuario.set_password(new_password)

            form.save()  # Guardar el usuario con los cambios
            messages.success(request, 'Usuario modificado correctamente!')
            return redirect('adminusuario')  

    context = {
        'form': form,
        'usuario': usuario
    }
    return render(request, "app/administrador/usuarios/manejo_usuario/adminmodificar.html", context)


def adminusuario(request):
    roles = TipoUsuario.objects.all()
    usuarios = Usuario.objects.all()

    rol_id = request.GET.get('rol')
    if rol_id:
        usuarios = usuarios.filter(tipo_usuario__codigo=rol_id)

    return render(request, "app/administrador/usuarios/manejo_usuario/adminusuario.html", {
        'usuarios': usuarios,
        'roles': roles,
    })

def eliminarUsuario(request, id):
    usuarios = Usuario.objects.get(id=id)
    usuarios.delete()
    return redirect(to="adminusuario")



def adminusuariohome(request):
           
    return render(request, "app/administrador/usuarios/adminusuariohome.html")
    

def admincursolistar(request):
    
    profesores = Usuario.objects.filter(tipo_usuario__tipo='Profesor')
    todos_los_cursos = Curso.objects.all()
    
    profesor_id = request.GET.get('profesor')
    materia_id = request.GET.get('materia')
    
    cursos = Curso.objects.all()
    
    if profesor_id:
        cursos = cursos.filter(profesor__id=profesor_id)
    
    if materia_id:
        cursos = cursos.filter(id=materia_id)
    
    context = {
        'cursos': cursos,
        'profesores': profesores,
        'todos_los_cursos': todos_los_cursos
    }
    

    return render(request, "app/administrador/cursos/agregar_cursos/admincursolistar.html", context)

def admincursoagregar(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El curso ha sido creado correctamente.')
            return redirect('admincursolistar')  
    else:
        form = CursoForm()      
    return render(request, "app/administrador/cursos/agregar_cursos/admincursoagregar.html", {'form': form})


def admincursomodificar(request, id):
 curso = Curso.objects.get(id=id)  

 if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso modificado correctamente!')
            return redirect('admincursolistar')  
 else:
        form = CursoForm(instance=curso)    
 return render(request, "app/administrador/cursos/agregar_cursos/admincursomodificar.html", {'form': form})


def eliminarcurso(request, id):
    usuarios = Usuario.objects.get(id=id)
    usuarios.delete()
    return redirect(to="admincursolistar")






def adminagregarprofesor(request):

    # Obtener solo los usuarios que sean profesores
    profesores = Usuario.objects.filter(tipo_usuario__tipo='Profesor')
    cursos = Curso.objects.all()

    if request.method == 'POST':
        profesor_id = request.POST.get('profesor')
        curso_id = request.POST.get('curso')

        # Verificar que ambos existan
        profesor = Usuario.objects.get(id=profesor_id)
        curso = Curso.objects.get(id=curso_id)

        # Asignar el curso al profesor
        curso.profesor = profesor
        curso.save()

        messages.success(request, f'El curso {curso.nombre} ha sido asignado al profesor {profesor.primer_nombre} {profesor.primer_apellido}.')
        return redirect('adminagregarprofesor')

    context = {
        'profesores': profesores,
        'cursos': cursos
    }
           
    return render(request, "app/administrador/usuarios/asignar_curso/adminagregarprofesor.html", context)


def adminunidadeslistar(request):

    # obtiene todos los datos primero
    profesores = Usuario.objects.filter(tipo_usuario__tipo='Profesor')
    cursos = Curso.objects.all()

    # Aqui obtiene todos los datos de la vista del listar
    profesor_id = request.GET.get('profesor')
    curso_id = request.GET.get('curso')

    # Filtra las cosas segun los filtros seleccionados
    unidades = Unidad.objects.all()

    if curso_id:
        unidades = unidades.filter(curso__id=curso_id)
    
    if profesor_id:
        unidades = unidades.filter(curso__profesor__id=profesor_id)

    context = {
        'unidades': unidades,
        'cursos': cursos,
        'profesores': profesores,
    }

    return render(request, "app/administrador/cursos/unidades/adminunidadeslistar.html", context)

def adminunidadesagregar(request):
    if request.method == 'POST':
        form = UnidadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminunidadeslistar')  
    else:
        form = UnidadForm()
    
    cursos = Curso.objects.all()  
    return render(request, "app/administrador/cursos/unidades/adminunidadesagregar.html", {'form': form, 'cursos': cursos})

def adminunidadesmodificar(request, id_unidad):
    unidad = Unidad.objects.get(id=id_unidad)  
    if request.method == 'POST':
        form = UnidadForm(request.POST, instance=unidad)  
        if form.is_valid():
            form.save()  
            return redirect('adminunidadeslistar')  
    else:
        form = UnidadForm(instance=unidad)  
    return render(request, "app/administrador/cursos/unidades/adminunidadesmodificar.html", {'form': form, 'unidad': unidad})



def adminunidadeseliminar(request, id_unidad):
    unidad = Unidad.objects.get(id=id_unidad)
    unidad.delete()
    messages.success(request, 'Unidad eliminada correctamente.')
    return redirect('adminunidadeslistar')



def adminagregaralumno(request):
    if request.method == 'POST':
        alumno_id = request.POST.get('alumno')  # Obtenemos el ID del alumno del formulario
        cursos_ids = request.POST.getlist('cursos')  # Obtenemos la lista de IDs de los cursos seleccionados

        try:
            alumno = Usuario.objects.get(id=alumno_id, tipo_usuario__tipo='Alumno')  # Obtenemos al alumno
            cursos = Curso.objects.filter(id__in=cursos_ids)  # Obtenemos los cursos seleccionados

            # Asignamos los cursos al alumno
            alumno.cursos.set(cursos)  # Si quieres reemplazar todos los cursos, usa set()
            alumno.save()

            messages.success(request, f'El alumno {alumno.primer_nombre} {alumno.primer_apellido} ha sido asignado a los cursos seleccionados.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Alumno no encontrado')
        except Curso.DoesNotExist:
            messages.error(request, 'Uno o más cursos no encontrados')

        return redirect('adminagregaralumno')  
    else:
        # Obtenemos la lista de alumnos y cursos para mostrarlos en el formulario
        alumnos = Usuario.objects.filter(tipo_usuario__tipo='Alumno')
        cursos = Curso.objects.all()

        context = {
            'alumnos': alumnos,
            'cursos': cursos
        }
        return render(request, 'app/administrador/usuarios/alumno_curso/adminagregaralumno.html', context)


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

                # Redirigir según el tipo de usuario
                if user.tipo_usuario.tipo == 'Profesor':
                    return redirect('profesorcurso', rut_profesor=user.rut)
                elif user.tipo_usuario.tipo == 'Alumno':
                    return redirect('alumnocurso', rut_alumno = user.rut)  
                elif user.tipo_usuario.tipo == 'Administrador':
                    return redirect('adminhome')  
                else:
                    return redirect('perfil')  

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