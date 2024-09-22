from django.urls import path
from .views import *

urlpatterns = [
    path('',index, name="index"),
    path('asistencia',asistencia, name= "asistencia"),
    path('horario', horario, name= "horario"),
    path('notas',notas,name ="notas"),
    path('calendario',calendario,name ="calendario"),
    path('profesorcurso',profesorcurso,name ="profesorcurso"),
    path('profesorhome',profesorhome,name ="profesorhome"),
    path('profesorasistencia',profesorasistencia,name ="profesorasistencia"),
    path('profesornotas',profesornotas,name ="profesornotas"),
    path('profesoranotacionlista',profesoranotacionlista,name ="profesoranotacionlista"),
    path('profesoranuncio',profesoranuncio,name ="profesoranuncio"),
    path('profesormaterial',profesormaterial,name ="profesormaterial"),
]