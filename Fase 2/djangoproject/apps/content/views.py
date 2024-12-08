# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import ContentForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.urls import reverse_lazy

from django.db import models
from cloudinary.models import CloudinaryField


class LocalFile(models.Model):
    file = models.FileField(upload_to='local_files/')  # Archivos locales

class CloudinaryFile(models.Model):
    file = CloudinaryField('file')  # Archivos en Cloudinary

def content_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    contents = Content.objects.filter(subject=subject)

    # Verificar si el usuario pertenece al grupo "teachers"
    is_teacher = request.user.groups.filter(name='Profesor').exists()

    return render(request, 'content/content_list.html', {
        'contents': contents,
        'subject': subject,
        'is_teacher': is_teacher
    })

def add_content(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)  # Incluye request.FILES
        if form.is_valid():
            content = form.save(commit=False)
            content.subject = subject
            content.save()
            
            # Procesar cada archivo subido
            if 'files' in request.FILES:
                for uploaded_file in request.FILES.getlist('files'):
                    # Crear instancia de archivo usando almacenamiento local
                    file_instance = File(file=uploaded_file)
                    file_instance.save()
                    content.files.add(file_instance)  # Asociar archivo al contenido

            content.save()  # Guardar el contenido completo
            return redirect('content_list', subject_id=subject.id)
    else:
        form = ContentForm()
    return render(request, 'content/add_content.html', {'form': form, 'subject': subject})


def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    files = content.files.all()  # Obtener todos los archivos asociados al contenido
    return render(request, 'content/content_detail.html', {'content': content, 'files': files})

class ContentDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Content
    template_name = "content/content_confirm_delete.html"
    success_message = "El contenido {} fue borrado"

    def get_success_url(self):
        # Obtener el subject_id desde el objeto Content
        return reverse_lazy("content_list", kwargs={"subject_id": self.object.subject.id})

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current:
            messages.warning(request, "Cannot delete content as it is set to current")
            return redirect("sessions")
        messages.success(self.request, self.success_message.format(obj.title))
        return super().delete(request, *args, **kwargs)