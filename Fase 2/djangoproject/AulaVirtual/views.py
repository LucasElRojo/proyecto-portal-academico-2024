from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'app/hijo.html')

def asistencia(request):
    return render(request, "app/asistencia.html")


def horario(request):
    return render(request, "app/horario.html")


def notas(request):
    return render(request, "app/notas.html")


def calendario(request):
    return render(request, "app/calendario.html")

# Vistas Profesor <------------------!
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