import random
import string
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from apps.corecode.models import Subject
from apps.students.models import Student
from apps.teachers.forms import AnnotationFilterForm, AnnotationForm, TeacherAnnotationForm

from .models import Annotation, Teacher


class TeacherListView(ListView):
    model = Teacher
    template_name = "teachers/teacher_list.html"

class TeacherDetailView(DetailView):
    model = Teacher
    template_name = "teachers/teacher_detail.html"


class TeacherCreateView(SuccessMessageMixin, CreateView):
    model = Teacher
    fields = [
        "estado", "rut", "apellido_paterno", "apellido_materno", "nombres",
        "sexo", "fecha_nacimiento", "fecha_admision", "telefono", "direccion", "observaciones", "email", "foto"
    ]
    success_message = "Profesor agregado correctamente!"
    success_url = reverse_lazy("teacher-list")
    
    def get_form(self):
        """add date picker in forms"""
        form = super(TeacherCreateView, self).get_form()
        form.fields["fecha_nacimiento"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["fecha_admision"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["direccion"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["observaciones"].widget = widgets.Textarea(attrs={"rows": 1})
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all()  # Pasar las asignaturas al contexto
        return context

    
    def form_valid(self, form):
        # Guardamos el estudiante primero
        response = super().form_valid(form)
        teacher = self.object  # El estudiante creado

        # Crear un usuario con el mismo RUT del estudiante
        username = teacher.rut
        email = teacher.email
        password = self.generate_random_password()

        # Crear el usuario en auth_user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=teacher.nombres,
            last_name=f"{teacher.apellido_paterno} {teacher.apellido_materno}",
            email=email,
        )

        # Asignar al grupo "Alumno"
        teacher_group = Group.objects.get(name="Profesor")
        user.groups.add(teacher_group)

        # Enviar contraseña por correo electrónico
        send_mail(
            "Tu cuenta ha sido creada",
            f"Tu usuario es {username} y tu contraseña es: {password}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Asignar asignaturas seleccionadas
        subject_ids = self.request.POST.get("subjects", "").split(",")
        subjects = Subject.objects.filter(id__in=subject_ids)
        teacher.subjects.set(subjects)

        messages.success(self.request, "Estudiante y usuario creados correctamente. Se ha enviado la contraseña por correo.")
        
        return response

    def generate_random_password(self, length=8):
        """Genera una contraseña aleatoria de longitud especificada."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))
    


class TeacherUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Teacher
    fields = [
        "estado", "rut", "apellido_paterno", "apellido_materno", "nombres",
        "sexo", "fecha_nacimiento", "fecha_admision", "telefono", "direccion", "observaciones", "email", "foto"
    ]
    success_message = "Registro actualizado correctamente."
    success_url = reverse_lazy("teacher-list")

    def get_form(self):
        """Add date picker in forms and make certain fields read-only."""
        form = super(TeacherUpdateView, self).get_form()
        
        form.fields["rut"].widget = forms.TextInput(
            attrs={
                "type": "text", 
                "readonly": "readonly", 
                "value": self.object.rut if self.object.rut else ""
            }
        )
        
        form.fields["fecha_nacimiento"].widget = forms.TextInput(
            attrs={
                "type": "text", 
                "readonly": "readonly", 
                "value": format(self.object.fecha_nacimiento, "d-m-Y") if self.object.fecha_nacimiento else ""
            }
        )
        
        form.fields["fecha_admision"].widget = forms.TextInput(
            attrs={
                "type": "text", 
                "readonly": "readonly", 
                "value": format(self.object.fecha_admision, "d-m-Y") if self.object.fecha_admision else ""
            }
        )

        form.fields["direccion"].widget = forms.Textarea(attrs={"rows": 2})
        form.fields["observaciones"].widget = forms.Textarea(attrs={"rows": 2})
        
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all()
        context['selected_subjects'] = self.object.subjects.values_list('id', flat=True)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        selected_subject_ids = set(int(id) for id in self.request.POST.get("subjects", "").split(",") if id)
        
        current_subject_ids = set(self.object.subjects.values_list("id", flat=True))

        subjects_to_add = selected_subject_ids - current_subject_ids
        subjects_to_remove = current_subject_ids - selected_subject_ids
        
        if subjects_to_add:
            self.object.subjects.add(*subjects_to_add)
        if subjects_to_remove:
            self.object.subjects.remove(*subjects_to_remove)

        return response


class TeacherDeleteView(DeleteView):
    model = Teacher
    success_url = reverse_lazy("teacher-list")
    
    def form_valid(self, form):
        teacher = self.get_object()
        
        try:
            user = User.objects.get(username=teacher.rut)
            user.delete()
        except User.DoesNotExist:
            pass
        return super().form_valid(form)

class TeacherSubjectsListView(ListView):
    model = Subject
    template_name = 'teachers/teacher_subjects.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        teacher_id = self.kwargs['pk']
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        return teacher.subjects.all() 

class SubjectDetailView(DetailView):
    model = Subject
    template_name = 'teachers/teacher_subjects_detail.html'
    context_object_name = 'subject'
    
class AnnotationListView(ListView):
    model = Annotation
    template_name = "teachers/teacher_annotation_list.html"
    context_object_name = "annotations"

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.GET.get("student")
        annotation_type = self.request.GET.get("type")

        if student_id:
            queryset = queryset.filter(student__id=student_id)
        if annotation_type:
            queryset = queryset.filter(annotation_type=annotation_type)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AnnotationFilterForm(self.request.GET)
        context["students"] = Student.objects.all()
        return context
    
class AnnotationCreateView(CreateView):
    model = Annotation
    form_class = AnnotationForm
    template_name = "teachers/teacher_annotation_form.html"
    success_url = reverse_lazy('annotation-list')
    

class TeacherAnnotationCreateView(CreateView):
    model = Annotation
    form_class = TeacherAnnotationForm
    template_name = "teachers/teacher_create_annotation_form.html"

    def get_initial(self):
        initial = super().get_initial()
        subject_id = self.kwargs.get("pk")
        subject = get_object_or_404(Subject, pk=subject_id)
        initial['subject'] = subject  # Pre-asignar el subject en el formulario
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs.get("pk")
        subject = get_object_or_404(Subject, pk=subject_id)
        context["subject"] = subject
        return context

    def form_valid(self, form):
        subject_id = self.kwargs.get("pk")
        subject = get_object_or_404(Subject, pk=subject_id)

        # Obtener el profesor basado en el username del usuario autenticado
        teacher_rut = self.request.user.username
        teacher = get_object_or_404(Teacher, rut=teacher_rut)
        
        # Asociar el subject y el teacher automáticamente
        form.instance.subject = subject
        form.instance.teacher = teacher

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("annotation-list")