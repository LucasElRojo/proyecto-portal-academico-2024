from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Group

class UsuarioManager(BaseUserManager):
    def create_user(self, rut, primer_nombre, primer_apellido, email, password=None, **extra_fields):
        if not rut:
            raise ValueError('El RUT es obligatorio.')
        if not email:
            raise ValueError('El email es obligatorio.')

        email = self.normalize_email(email)
        user = self.model(
            rut=rut,
            primer_nombre=primer_nombre,
            primer_apellido=primer_apellido,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, primer_nombre, primer_apellido, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(rut, primer_nombre, primer_apellido, email, password, **extra_fields)

class TipoUsuario(models.Model):
    codigo = models.IntegerField(null=False, primary_key=True)
    tipo = models.CharField(max_length=50)
    created_ad = models.DateField(auto_now_add=True)
    updated_ad = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.tipo

class Usuario(AbstractBaseUser):
    rut = models.CharField(max_length=12, unique=True)
    password = models.CharField(max_length=128)
    primer_nombre = models.CharField(max_length=120)
    segundo_nombre = models.CharField(max_length=120, blank=True, null=True)
    primer_apellido = models.CharField(max_length=120)
    segundo_apellido = models.CharField(max_length=120, blank=True, null=True)
    email = models.EmailField(max_length=120, unique=True)
    telefono = models.IntegerField()
    
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.SET_NULL, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['primer_nombre', 'primer_apellido', 'email', 'telefono']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"
    

    # Métodos para manejar permisos
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


