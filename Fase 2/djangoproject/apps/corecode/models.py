from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
# Create your models here.


class SiteConfig(models.Model):
    """Site Configurations"""

    key = models.SlugField()
    value = models.CharField(max_length=200)

    def __str__(self):
        return self.key


class AcademicSession(models.Model):
    """Academic Session"""

    name = models.CharField(max_length=200, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class AcademicTerm(models.Model):
    """Academic Term"""

    name = models.CharField(max_length=20, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Subject"""

    name = models.CharField(max_length=200, unique=True, verbose_name="Nombre")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Attendance(models.Model):
    """Registro de asistencia por asignatura y estudiante"""
    ATTENDANCE_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('justificado', 'Justificado'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=12, choices=ATTENDANCE_CHOICES, default='ausente')

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ["date"]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.status}"

class StudentClass(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Announcement(models.Model):
    
    USER_TYPE_CHOICES = [
        ('global', 'Global'),           
        ('teacher', 'Profesor'),        
        ('student', 'Estudiante'),      
        ('representative', 'Representante'),  
    ]

    title = models.CharField(max_length=255)                     
    content = RichTextField()                           
    created_at = models.DateTimeField(default=timezone.now)      
    target_user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='global')  
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, related_name="announcements")  

    def __str__(self):
        return self.title