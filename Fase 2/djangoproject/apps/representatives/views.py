import random
import string

from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .models import Representatives


class RepresentativesListView(ListView):
    model = Representatives
    template_name = "representatives/representatives_list.html"

class RepresentativesDetailView(DetailView):
    model = Representatives
    template_name = "representatives/representatives_detail.html"


class RepresentativesCreateView(SuccessMessageMixin, CreateView):
    model = Representatives
    fields = "__all__"
    success_message = "Apoderado agregado correctamente!"
    success_url = reverse_lazy("teacher-list")
    
    def get_form(self):
        """add date picker in forms"""
        form = super(RepresentativesCreateView, self).get_form()
        form.fields["fecha_nacimiento"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["fecha_admision"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["direccion"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["observaciones"].widget = widgets.Textarea(attrs={"rows": 1})
        return form
    
    def form_valid(self, form):
        # Guardamos el estudiante primero
        response = super().form_valid(form)
        Representatives = self.object  # El estudiante creado

        # Crear un usuario con el mismo RUT del estudiante
        username = Representatives.rut
        email = Representatives.email
        password = self.generate_random_password()

        # Crear el usuario en auth_user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=Representatives.nombres,
            last_name=f"{Representatives.apellido_paterno} {Representatives.apellido_materno}",
            email=email,
        )

        # Asignar al grupo "Alumno"
        representatives_group = Group.objects.get(name="Apoderado")
        user.groups.add(representatives_group)

        # Enviar contraseña por correo electrónico
        send_mail(
            "Tu cuenta ha sido creada",
            f"Tu usuario es {username} y tu contraseña es: {password}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        messages.success(self.request, "Estudiante y usuario creados correctamente. Se ha enviado la contraseña por correo.")
        
        return response

    def generate_random_password(self, length=8):
        """Genera una contraseña aleatoria de longitud especificada."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))
    


class RepresentativesUpdateView(SuccessMessageMixin, UpdateView):
    model = Representatives
    fields = "__all__"
    success_message = "Record successfully updated."

    def get_form(self):
        """add date picker in forms"""
        form = super(RepresentativesUpdateView, self).get_form()
        form.fields["fecha_nacimiento"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["fecha_admision"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["direccion"].widget = widgets.Textarea(attrs={"rows": 2})
        form.fields["observaciones"].widget = widgets.Textarea(attrs={"rows": 2})
        # form.fields['passport'].widget = widgets.FileInput()
        return form


class RepresentativesDeleteView(DeleteView):
    model = Representatives
    success_url = reverse_lazy("representatives-list")
