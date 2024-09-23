from django.db import models

# Create your models here.


class usuario (models.Model):
    rut = models.IntegerField
    contrasena = models.CharField(max_length=128)


class profesor (models.Model):
    primer_nombre = models.CharField(max_length=120)
    segundo_nombre = models.CharField(max_length=120)
    primer_apellido = models.CharField(max_length=120)
    segundo_apellido = models.CharField(max_length=120)
    email = models.EmailField(max_length=150)
    telefono = models.IntegerField


class administrador (models.Model):
    primer_nombre = models.CharField(max_length=120)
    segundo_nombre = models.CharField(max_length=120)
    primer_apellido = models.CharField(max_length=120)
    segundo_apellido = models.CharField(max_length=120)
    email = models.EmailField(max_length=150)
    telefono = models.IntegerField


class apoderado (models.Model):
    primer_nombre = models.CharField(max_length=120)
    segundo_nombre = models.CharField(max_length=120)
    primer_apellido = models.CharField(max_length=120)
    segundo_apellido = models.CharField(max_length=120)
    email = models.EmailField(max_length=150)
    telefono = models.IntegerField


class alumno (models.Model):
    primer_nombre = models.CharField(max_length=120)
    segundo_nombre = models.CharField(max_length=120)
    primer_apellido = models.CharField(max_length=120)
    segundo_apellido = models.CharField(max_length=120)
    email = models.EmailField(max_length=150)
    telefono = models.IntegerField
    direccion = models.CharField(max_length=120)
    fecha_nacimiento = models.DateField
    apoderado = models.ForeignKey(apoderado, on_delete=models.CASCADE)

class curso (models.Model):
    id_curso = models.CharField(max_length=100)
    fecha = models.DateField
    nombre_ano = models.IntegerField

class Sala (models.Model):
    id_sala= models.IntegerField(null = False,primary_key=True)
    codigo = models.CharField(max_length=100)

class asignatura (models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=150)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    curso = models.ForeignKey(curso, on_delete=models.CASCADE)
    profesor = models.ForeignKey(profesor, on_delete=models.CASCADE)

class nota (models.Model):
    nota = models.IntegerField
    fecha = models.DateField
    alumno = models.ForeignKey(alumno, on_delete=models.CASCADE)


class anotaciones (models.Model):
    descripcion = models.CharField(max_length=120)
    fecha = models.DateField
    alumno = models.ForeignKey(alumno, on_delete=models.CASCADE)


class asistencia (models.Model):
    fecha = models.DateField
    estado = models.CharField(max_length=20)
    alumno = models.ForeignKey(alumno, on_delete=models.CASCADE)

class inscripcion (models.Model):
    id_inscripcion = models.IntegerField
    alumno = models.ForeignKey(alumno, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(asignatura, on_delete=models.CASCADE)

class horario (models.Model):
    dia = models.CharField(max_length=120)
    hora_inicio = models.DateField
    hora_fin = models.DateField
    asignatura = models.ForeignKey(asignatura, on_delete=models.CASCADE)

class anuncios (models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=1000)
    fecha = models.DateField
    asignatura = models.ForeignKey(asignatura, on_delete=models.CASCADE)

class material (models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=800)
    enlace = models.CharField(max_length=200)
    fecha = models.DateField
    asignatura = models.ForeignKey(asignatura, on_delete=models.CASCADE)


class calendario_de_pruebas (models.Model):
    fecha = models.DateField
    descripcion = models.CharField(max_length=800)
    asignatura = models.ForeignKey(asignatura, on_delete=models.CASCADE)












