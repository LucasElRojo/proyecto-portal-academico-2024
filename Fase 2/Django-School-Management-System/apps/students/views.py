import csv
import random
import string

from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django import forms
from django.utils.dateformat import format

from apps.corecode.models import Attendance, Subject
from apps.finance.models import Invoice

from .models import Student, StudentBulkUpload


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"

    def get_context_data(self, **kwargs):
        context = super(StudentDetailView, self).get_context_data(**kwargs)
        context["payments"] = Invoice.objects.filter(student=self.object)
        return context


class StudentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    fields = [
        "estado", "rut", "apellido_paterno", "apellido_materno", "nombres",
        "sexo", "fecha_nacimiento", "fecha_admision", "curso_actual",
        "representante", "telefono_apoderado", "direccion", "observaciones", "email", "foto"
    ]
    success_message = "Estudiante agregado correctamente."
    success_url = reverse_lazy("student-list")

    def get_form(self):
        form = super(StudentCreateView, self).get_form()
        form.fields["fecha_nacimiento"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["fecha_admision"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["direccion"].widget = widgets.Textarea(attrs={"rows": 2})
        form.fields["observaciones"].widget = widgets.Textarea(attrs={"rows": 2})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all()  # Pasar las asignaturas al contexto
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        student = self.object  # El estudiante creado

        # Crear un usuario con el mismo RUT del estudiante
        username = student.rut
        email = student.email
        password = self.generate_random_password()

        # Crear el usuario en auth_user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=student.nombres,
            last_name=f"{student.apellido_paterno} {student.apellido_materno}",
            email=email,
        )

        # Asignar al grupo "Alumno"
        alumno_group = Group.objects.get(name="Alumno")
        user.groups.add(alumno_group)

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
        student.subjects.set(subjects)

        messages.success(self.request, "Estudiante y usuario creados correctamente. Se ha enviado la contraseña por correo.")
        
        return response

    def generate_random_password(self, length=8):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))



class StudentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    fields = [
        "estado", "rut", "apellido_paterno", "apellido_materno", "nombres",
        "sexo", "fecha_nacimiento", "fecha_admision", "curso_actual",
        "representante", "telefono_apoderado", "direccion", "observaciones", "email", "foto"
    ]
    success_message = "Registro actualizado correctamente."
    success_url = reverse_lazy("student-list")

    def get_form(self):
        """Add date picker in forms and make certain fields read-only."""
        form = super(StudentUpdateView, self).get_form()
        
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







class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    success_url = reverse_lazy("student-list")

    def form_valid(self, form):
        student = self.get_object()
        
        try:
            user = User.objects.get(username=student.rut)
            user.delete()
        except User.DoesNotExist:
            pass
        
        return super().form_valid(form)


class StudentBulkUploadView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentBulkUpload
    template_name = "students/students_upload.html"
    fields = ["csv_file"]
    success_url = "/student/list"
    success_message = "Successfully uploaded students"


class DownloadCSVViewdownloadcsv(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_template.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "registration_number",
                "surname",
                "firstname",
                "other_names",
                "gender",
                "parent_number",
                "address",
                "current_class",
            ]
        )

        return response
    
class AttendanceListView(ListView):
    model = Attendance
    template_name = "students/student_attendance_list.html"
    context_object_name = "attendances"
    
    def get_queryset(self):
        return Attendance.objects.select_related('student', 'subject').order_by('date')