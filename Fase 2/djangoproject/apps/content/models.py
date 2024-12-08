# models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from apps.corecode.models import Subject
from ckeditor.fields import RichTextField


from django.core.files.storage import FileSystemStorage

local_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

class Content(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    description = RichTextField()
    files = models.ManyToManyField('File', related_name='contents') # Relación de múltiples archivos

    def str(self):
        return self.title


class File(models.Model):
    file = models.FileField(storage=local_storage, upload_to='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.file.name