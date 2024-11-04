from django.core.validators import RegexValidator, EmailValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Staff(models.Model):
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
        return f"{self.apellido_paterno} {self.apellido_materno} {self.nombres} ({self.rut})"

    def get_absolute_url(self):
        return reverse("staff-detail", kwargs={"pk": self.pk})
