from django.urls import path
from .views import *

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

    path('profesorcurso/<rut_profesor>/', profesorcurso, name ="profesorcurso"),
    path('profesorhome/<int:id_curso>/', profesorhome, name ="profesorhome"),
    path('profesorasistencia/', profesorasistencia, name ="profesorasistencia"),
    path('profesornotas/', profesornotas, name ="profesornotas"),
    path('profesoranotacionlista/', profesoranotacionlista, name ="profesoranotacionlista"),
    path('profesoranuncio/', profesoranuncio, name ="profesoranuncio"),
    path('curso/<int:id_curso>/material/', profesormaterial, name="profesormaterial"),
    path('unidad/<int:unidad_id>/agregar/', agregar_contenido, name='agregar_contenido'),

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