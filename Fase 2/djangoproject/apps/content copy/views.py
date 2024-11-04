# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import ContentForm
from django.http import JsonResponse
from django.template.loader import render_to_string

def content_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    contents = Content.objects.filter(subject=subject)
    return render(request, 'content/content_list.html', {'contents': contents, 'subject': subject})

def add_content(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.subject = subject
            content.save()
            # Guardar cada archivo subido en la relación de archivos
            for uploaded_file in request.FILES.getlist('files'):
                file_instance = File(file=uploaded_file)
                file_instance.save()
                content.files.add(file_instance)
            return redirect('content_list', subject_id=subject.id)
    else:
        form = ContentForm()
    return render(request, 'content/add_content.html', {'form': form, 'subject': subject})


def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    files = content.files.all()  # Obtener todos los archivos asociados al contenido
    return render(request, 'content/content_detail.html', {'content': content, 'files': files})
