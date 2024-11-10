import random
import string

from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .models import Representatives
from apps.students.models import Student
from apps.students.models import Subject


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



    
class RepresentativeListView(ListView):
    template_name = 'representatives/representatives_student.html'
    model = Representatives
    context_object_name = 'students'

    def get_queryset(self):
        # Filtra los estudiantes que pertenecen al representante actual
        representative_id = self.kwargs['pk']
        return Student.objects.filter(representante__id=representative_id)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Incluye el representante en el contexto para usarlo en el template
        context['representative'] = Representatives.objects.get(pk=self.kwargs['pk'])
        return context






class RepresentativeStudentDetailView(DetailView):
    template_name = 'representatives/representatives_student_detail.html'
    context_object_name = 'student'
    model = Student

    def get_object(self):
        # Obtiene el estudiante solo si pertenece al representante correcto
        representative_id = self.kwargs['representative_pk']
        student_id = self.kwargs['student_pk']
        return get_object_or_404(Student, pk=student_id, representante__id=representative_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        representative = get_object_or_404(Representatives, pk=self.kwargs['representative_pk'])
        context['representative'] = representative
        context['subjects'] = self.object.subjects.all()  # Todos los subjects del estudiante

        # Selecciona un subject específico o usa el primero disponible
        subject_id = self.request.GET.get('subject_id')
        if subject_id:
            subject = get_object_or_404(Subject, pk=subject_id)
        else:
            subject = self.object.subjects.first()  # Selecciona el primer subject si no se especifica  
        
        if subject:
            context['selected_subject'] = subject
            context['annotations'] = subject.annotations.all()  
            context['content_list'] = subject.contents.all()
        else:
            # Manejo del caso donde no hay subjects disponibles
            context['selected_subject'] = None
            context['annotations'] = []
            context['content_list'] = []

        return context

        


class RepresentativeContentView(DetailView):
    template_name = 'representatives/representatives_content.html'
    model = Representatives
    context_object_name = 'representative'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todos los estudiantes asociados al representante
        students = Student.objects.filter(representante=self.object)

        # Obtener todas las asignaturas relacionadas con los estudiantes del representante
        subjects = Subject.objects.filter(students__in=students).distinct()  # Asegúrate de que "students" es el campo de relación
        context['subjects'] = subjects

        # Filtrar por asignatura seleccionada
        subject_id = self.request.GET.get('subject_id')
        if subject_id:
            selected_subject = get_object_or_404(Subject, pk=subject_id)
            context['selected_subject'] = selected_subject
            context['contents'] = selected_subject.contents.all()  # Asegúrate de que 'contents' es el nombre correcto de la relación de contenidos en Subject
        else:
            context['selected_subject'] = None
            context['contents'] = []

        return context