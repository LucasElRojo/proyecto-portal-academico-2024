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

class Curso(models.Model):
    nombre = models.CharField(max_length=255)
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario__tipo': 'Profesor'})  
    alumnos = models.ManyToManyField(Usuario, related_name="cursos", limit_choices_to={'tipo_usuario__tipo': 'Alumno'})  
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return self.nombre


class Anotacion(models.Model):
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario__tipo': 'Alumno'})
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="anotaciones", limit_choices_to={'tipo_usuario__tipo': 'Profesor'})
    comentario = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    positiva = models.BooleanField(default=True)

    def __str__(self):
        return f"Anotación de {self.profesor} a {self.alumno} en {self.curso}"
    


class Unidad(models.Model):
    nombre = models.CharField(max_length=255)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Recurso(models.Model):
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='media/')  

    def __str__(self):
        return self.descripcion
    


class Anuncio(models.Model):
    titulo = models.CharField(max_length=255)
    asignatura = models.CharField(max_length=100)
    profesor = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)
    comentarios = models.TextField()
    archivo = models.FileField(upload_to='anuncios/', blank=True, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
    