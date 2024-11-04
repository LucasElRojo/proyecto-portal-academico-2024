from django.core.validators import RegexValidator, EmailValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Representatives(models.Model):
    STATUS = [("activo", "Activo"), ("inactivo", "Inactivo")]

    GENDER = [("masculino", "Masculino"), ("femenino", "Femenino")]
    rut_regex = RegexValidator(
        regex=r"^\d{1,2}\d{3}\d{3}-[0-9kK]{1}$",
        message="El RUT debe estar en el formato 'XXXXXXXX-X'"
    )
    rut = models.CharField(max_length=12, unique=True, validators=[rut_regex], blank=True)
    estado = models.CharField(max_length=10, choices=STATUS, default="activo")
    apellido_paterno = models.CharField(max_length=200)
    apellido_materno = models.CharField(max_length=200)
    nombres = models.CharField(max_length=200, blank=True)
    sexo = models.CharField(max_length=10, choices=GENDER, default="masculino")
    fecha_nacimiento = models.DateField(default=timezone.now)
    fecha_admision = models.DateField(default=timezone.now)

    telefono_regex = RegexValidator(
        regex="^[0-9]{9,15}$", message="El número de teléfono no tiene el formato correcto."
    )
    telefono = models.CharField(
        validators=[telefono_regex], max_length=15, blank=True
    )
    direccion = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    email = models.EmailField(
        max_length=254, unique=True, validators=[EmailValidator()],
        blank=True, null=True
    )
    foto = models.ImageField(blank=True, upload_to="students/fotos/")

    class Meta:
        ordering = ["apellido_paterno", "apellido_materno", "nombres"]

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    def get_estudiantes(self):
        """Devuelve todos los estudiantes asociados a este apoderado"""
        return self.estudiantes.all()
    
    def get_num_estudiantes(self):
        """Devuelve la cantidad de estudiantes asociados a este representante"""
        return self.estudiantes.count()  # Usa el related_name "estudiantes"