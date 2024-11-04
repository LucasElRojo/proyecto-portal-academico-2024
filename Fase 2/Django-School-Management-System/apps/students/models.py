from itertools import cycle
from django.core.validators import RegexValidator, EmailValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.corecode.models import StudentClass, AcademicTerm, Subject


from django.core.exceptions import ValidationError

class Student(models.Model):
    STATUS_CHOICES = [("activo", "Activo"), ("inactivo", "Inactivo")]
    GENDER_CHOICES = [("masculino", "Masculino"), ("femenino", "Femenino")]

    estado = models.CharField(max_length=10, choices=STATUS_CHOICES, default="activo")
    rut_regex = RegexValidator(
        regex=r"^\d{1,2}\d{3}\d{3}-[0-9kK]{1}$",
        message="El RUT debe estar en el formato 'XXXXXXXX-X'"
    )
    rut = models.CharField(max_length=12, unique=True, validators=[rut_regex], blank=True)
    apellido_paterno = models.CharField(max_length=200)
    apellido_materno = models.CharField(max_length=200)
    nombres = models.CharField(max_length=200, blank=True)
    sexo = models.CharField(max_length=10, choices=GENDER_CHOICES, default="masculino")
    fecha_nacimiento = models.DateField(default=timezone.now)
    curso_actual = models.ForeignKey(
        StudentClass, on_delete=models.SET_NULL, blank=True, null=True
    )
    fecha_admision = models.DateField(default=timezone.now)
    telefono_regex = RegexValidator(
        regex="^[0-9]{9,15}$", message="El número de teléfono no tiene el formato correcto."
    )
    telefono_apoderado = models.CharField(
        validators=[telefono_regex], max_length=15, blank=True
    )
    direccion = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    email = models.EmailField(
        max_length=254, unique=True, validators=[EmailValidator()],
        blank=True, null=True
    )
    foto = models.ImageField(blank=True, upload_to="students/fotos/")

    # Relación de uno a muchos con el apoderado
    representante = models.ForeignKey(
        "representatives.Representatives", on_delete=models.SET_NULL, null=True, blank=True, related_name="estudiantes"
    )
    
    subjects = models.ManyToManyField(Subject, related_name="students", blank=True)
    
    class Meta:
        ordering = ["apellido_paterno", "apellido_materno", "nombres"]

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"




class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="students/bulkupload/")
