# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from apps.corecode.models import Subject
from ckeditor.fields import RichTextField

class Content(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    description = RichTextField()
    files = models.ManyToManyField('File', related_name='contents')  # Relación de múltiples archivos

    def __str__(self):
        return self.title

class File(models.Model):
    file = models.FileField(upload_to='media/contents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name