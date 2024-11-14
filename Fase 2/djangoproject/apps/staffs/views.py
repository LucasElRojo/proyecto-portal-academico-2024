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




from django.utils.decorators import method_decorator
from apps.corecode.decorators import  teacher_required,  teacher_or_staff_required

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

class StaffAnnouncementCreateView(CreateView):
    model = Announcement
    template_name = "staffs/staff_announcement_form.html"
    fields = ['title', 'content']  # Solo título y contenido
    success_url = reverse_lazy('staff_announcements')

    def form_valid(self, form):
        
        form.instance.target_user_type = 'global'  
        response = super().form_valid(form)  

        
        teacher_emails = list(Teacher.objects.values_list('email', flat=True))
        student_emails = list(Student.objects.values_list('email', flat=True))
        representative_emails = list(Representatives.objects.values_list('email', flat=True))
        staff_emails = list(Staff.objects.values_list('email', flat=True))

        # Combinar todos los correos en una sola lista
        recipient_list = teacher_emails + student_emails + representative_emails + staff_emails

        # Enviar el correo a todos los destinatarios
        try:
            send_mail(
                subject=f"{form.instance.title}",
                message=form.instance.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            messages.success(self.request, "Anuncio creado y correos enviados correctamente.")
        except Exception as e:
            messages.error(self.request, f"Anuncio creado, pero hubo un error al enviar los correos: {e}")

        return response