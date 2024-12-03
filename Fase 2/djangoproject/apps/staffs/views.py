from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.contrib import messages
import string
import random

from .models import Staff
from apps.corecode.models import Announcement

from apps.students.models import  Student
from apps.teachers.models import Teacher
from apps.representatives.models import Representatives

from django.core.mail import EmailMultiAlternatives


from django.utils.decorators import method_decorator
from apps.corecode.decorators import  teacher_required,  teacher_or_staff_required

import base64
from pathlib import Path
from bs4 import BeautifulSoup
from django.conf import settings



class StaffListView(ListView):
    model = Staff


class StaffDetailView(DetailView):
    model = Staff
    template_name = "staffs/staff_detail.html"


class StaffCreateView(SuccessMessageMixin, CreateView):
    model = Staff
    fields = "__all__"
    success_message = "Nuevo administrador agregado correctamente!"
    success_url = reverse_lazy("staff-list") 

    def get_form(self):
        """Add date picker in forms."""
        form = super(StaffCreateView, self).get_form()
        form.fields["fecha_nacimiento"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["fecha_admision"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["direccion"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["observaciones"].widget = widgets.Textarea(attrs={"rows": 1})
        return form

    def form_valid(self, form):
        # Guardamos el administrador primero
        response = super().form_valid(form)
        staff = self.object  # El administrador creado

        # Crear un usuario con el mismo RUT del administrador
        username = staff.rut
        email = staff.email
        password = self.generate_random_password()

        # Crear el usuario en auth_user con permisos de staff
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=staff.nombres,
            last_name=f"{staff.apellido_paterno} {staff.apellido_materno}",
            email=email,
            is_staff=True  # Otorga permisos de staff
        )

        # Asignar al grupo "Administrador"
        admin_group = Group.objects.get(name="Administrador")
        user.groups.add(admin_group)

        # Enviar contraseña por correo electrónico
        send_mail(
            "Tu cuenta ha sido creada",
            f"Tu usuario es {username} y tu contraseña es: {password}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        messages.success(self.request, "Administrador y usuario creados correctamente. Se ha enviado la contraseña por correo.")
        
        return response

    def generate_random_password(self, length=8):
        """Genera una contraseña aleatoria de longitud especificada."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))


class StaffUpdateView(SuccessMessageMixin, UpdateView):
    model = Staff
    fields = "__all__"
    success_message = "Record successfully updated."

    def get_form(self):
        """add date picker in forms"""
        form = super(StaffUpdateView, self).get_form()
        form.fields["fecha_nacimiento"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["fecha_admision"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["direccion"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["observaciones"].widget = widgets.Textarea(attrs={"rows": 1})
        return form


class StaffDeleteView(DeleteView):
    model = Staff
    success_url = reverse_lazy("staff-list")




class StaffAnnouncementListView(ListView):
    model = Announcement
    template_name = "staffs/staff_announcement_list.html"
    context_object_name = "announcements"

    def get_queryset(self):
        # Filtra solo anuncios globales
        return  Announcement.objects.filter(target_user_type='global').order_by('-created_at')
    


def embed_images_in_email(content):
    """
    Convierte las imágenes en URLs Base64 dentro del contenido HTML.
    """
    soup = BeautifulSoup(content, "html.parser")  # Analizar el HTML

    for img in soup.find_all("img"):  # Buscar etiquetas <img>
        img_src = img.get("src")
        if img_src.startswith("/media/"):  # Si la imagen está en el directorio de media
            # Ruta completa de la imagen en el sistema de archivos
            image_path = Path(settings.MEDIA_ROOT) / img_src.lstrip("/media/")
            try:
                with open(image_path, "rb") as img_file:
                    # Codificar la imagen en base64
                    encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
                    mime_type = f"image/{image_path.suffix.lstrip('.')}"  # Detectar tipo MIME
                    # Reemplazar la URL con datos Base64
                    img["src"] = f"data:{mime_type};base64,{encoded_image}"
            except FileNotFoundError:
                print(f"Imagen no encontrada: {image_path}")
    return str(soup)  # Retornar el contenido HTML modificado

class StaffAnnouncementCreateView(CreateView):
    model = Announcement
    template_name = "staffs/staff_announcement_form.html"
    fields = ['title', 'content', 'image']  # Incluimos el campo 'image' en los campos del formulario
    success_url = reverse_lazy('staff_announcements')

    def form_valid(self, form):
        # Configuración del anuncio
        form.instance.target_user_type = 'global'
        response = super().form_valid(form)

        # Obtener los correos electrónicos
        teacher_emails = list(Teacher.objects.values_list('email', flat=True))
        student_emails = list(Student.objects.values_list('email', flat=True))
        representative_emails = list(Representatives.objects.values_list('email', flat=True))
        staff_emails = list(Staff.objects.values_list('email', flat=True))
        recipient_list = teacher_emails + student_emails + representative_emails + staff_emails

        # Convertir el contenido HTML a Base64 e incluir imágenes embebidas
        raw_html_content = form.instance.content  # Contenido de CKEditor
        html_content = embed_images_in_email(raw_html_content)  # Procesar imágenes embebidas

        # Enviar el correo con contenido HTML
        subject = form.instance.title
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body="Este correo incluye un anuncio global. Por favor, habilita HTML para ver el contenido completo.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )
            email.attach_alternative(html_content, "text/html")  # HTML con imágenes embebidas

            # Adjuntar la imagen cargada al correo si existe
            if form.instance.image:
                image_url = form.instance.image.url  # Obtener la URL de la imagen de Cloudinary
                email.attach(
                    form.instance.image.name,  # Nombre de la imagen
                    form.instance.image.file.read(),  # Contenido de la imagen
                    "image/png"  # Tipo MIME
                )

            email.send()
            messages.success(self.request, "Anuncio creado y correos enviados correctamente.")
        except Exception as e:
            messages.error(self.request, f"Anuncio creado, pero hubo un error al enviar los correos: {e}")

        return response