from django.urls import path
from .views import *
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name="index"),
    path('perfil/', perfil, name="perfil"),
    path('anotaciones/', anotaciones, name="anotaciones"),
    path('anuncios/', anuncios, name="anuncios"),
    path('hijo/', hijo, name= "hijo"),
    path('asistencia/',asistencia, name= "asistencia"),
    path('horario/', horario, name= "horario"),
    path('notas/', notas, name ="notas"),
    path('calendario/', calendario, name ="calendario"),

    #Vistas alumno

    # ------- urls principales alumno---------------
    path('alumnocurso/<rut_alumno>/', alumnocurso, name="alumnocurso"),
    path('alumnohome/<id_curso>/', alumnohome, name="alumnohome"),

    # ------- urls aprtado material---------------
    path('alumnohome/<id_curso>/', alumnohome, name="alumnohome"),
    
    # ------- urls aprtado anotacion---------------
    path('alumnoanotacion/<rut_alumno>/', alumnoanotacion, name="alumnoanotacion"),

    # ------- urls aprtado notas---------------
    path('alumnonotas/<rut_alumno>/', alumnonotas, name='alumnonotas'),

    # ------- urls aprtado anuncio---------------
    path('alumnoanuncio/<rut_alumno>/', alumnoanuncio, name="alumnoanuncio"),

    # ------- urls aprtado material---------------
    path('alumnomaterial/<rut_alumno>/<id_curso>/', alumnomaterial, name="alumnomaterial"),

    # ------- urls aprtado Asistencia---------------
    path('detalle_clase/<id_curso>/', detalle_clase, name="detalle_clase"),

    #Vistas profesor

    # ------- urls principales profesor---------------
    path('profesorcurso/<rut_profesor>/', profesorcurso, name ="profesorcurso"),
    path('profesorhome/<id_curso>/', profesorhome, name ="profesorhome"),
    path('profesorasistencia/', profesorasistencia, name ="profesorasistencia"),

    # ------- Profesor apartado notas  ---------------
    path('profesornotas/<id_curso>/', profesornotas, name ="profesornotas"),
    path('agregarnota/<id_curso>/', agregarnota, name='agregarnota'),

    # ------- Profesor apartado asistencia  ---------------
    path('profesor/cursos/<int:curso_id>/clase/nueva_tomar_asistencia/', crear_clase_y_tomar_asistencia, name='crear_clase_y_tomar_asistencia'),
    
    # ------- Profesor apartado Anotacion  ---------------
    path('profesoranotacionlista/profesor/<rut_profesor>/curso/<int:id_curso>/', profesoranotacionlista, name='profesoranotacionlista'),
    path('profesoranotacion/<id_alumno>/', profesoranotacion, name ="profesoranotacion"),
    path('profesorcrearanotacion/<id_alumno>/<id_curso>/', profesorcrearanotacion, name='profesorcrearanotacion'),
    path('profesobservaranotacion/alumno/<id_alumno>/curso/<int:id_curso>/', profesobservaranotacion, name='profesobservaranotacion'),

    # ------- Profesor apartado Anuncio  ---------------
    path('profesoranuncio/<id_curso>/', profesoranuncio, name="profesoranuncio"),
    path('profesoragregaranuncio/<id_curso>/', profesoragregaranuncio, name='profesoragregaranuncio'),

    # ------- Profesor apartado Material  ---------------
    path('curso/<id_curso>/material/', profesormaterial, name="profesormaterial"),
    path('unidad/<unidad_id>/agregar/', agregar_contenido, name='agregar_contenido'),

    path('adminhome/', adminhome, name ="adminhome"),
    path('admincursos/', admincursos, name ="admincursos"),
    path('adminusuario/', adminusuario, name ="adminusuario"),
    path('adminprofe/', adminprofe, name ="adminprofe"),
    path('adminagregar/', adminagregar, name ="adminagregar"),
    path('adminmodificar/<id>/',adminmodificar, name="adminmodificar"),
    path('eliminarUsuario/<id>/',eliminarUsuario, name="eliminarUsuario"),
    path('agregar/<id>/',eliminarUsuario, name="eliminarUsuario"),
    
    path('registro/', registro_view, name='registro'),
    path('login/', login_view, name='login'),
    path('cambiar-password/', cambiar_password_view, name='cambiar_password'),
    path('recuperar-password/', recuperar_password_view, name='recuperar_password'),
    path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  #<----------- Sirve para que los archivos guardados puedan descargarse 