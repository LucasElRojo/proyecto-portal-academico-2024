import csv
import random
import string
import pandas as pd

from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django import forms
from django.utils.dateformat import format

from apps.corecode.models import Attendance, StudentClass, Subject
from apps.finance.models import Invoice
from apps.representatives.models import Representatives

from .models import Student, StudentBulkUpload


import json
from django.utils.dateparse import parse_datetime, parse_date
from django.http import JsonResponse
from django.shortcuts import render
from apps.teachers.models import Event
from apps.corecode.models import Announcement


from django.utils.decorators import method_decorator
from apps.corecode.decorators import  teacher_required, staff_or_superuser_required, teacher_or_staff_required



@method_decorator(staff_or_superuser_required, name='dispatch')
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
    
    
    
## CSV

def upload_student_excel(request):
    if request.method == "POST" and request.FILES["file"]:
        excel_file = request.FILES["file"]
        try:
            df = pd.read_excel(excel_file, engine="openpyxl")
            for _, row in df.iterrows():
                rut = row["rut"]
                nombres = row["nombres"]
                apellido_paterno = row["apellido_paterno"]
                apellido_materno = row["apellido_materno"]
                sexo = row["sexo"]
                fecha_nacimiento = row["fecha_nacimiento"]
                fecha_admision = row["fecha_admision"]
                telefono_apoderado = row["telefono_apoderado"]
                direccion = row["direccion"]
                observaciones = row["observaciones"]
                email = row["email"]

                # Recuperar el curso actual
                curso_actual_name = row["curso_actual"]
                curso = StudentClass.objects.filter(name=curso_actual_name).first()

                # Recuperar el Subject
                subject_name = row["asignatura"]
                subject = Subject.objects.filter(name=subject_name).first()

                # Recuperar el Representatives
                representante_rut = row["representante"]
                representante = Representatives.objects.filter(rut=representante_rut).first()

                # Validaciones
                if not curso:
                    messages.error(request, f"Curso '{curso_actual_name}' no encontrado.")
                    continue

                if not subject:
                    messages.error(request, f"Asignatura '{subject_name}' no encontrada.")
                    continue

                if not representante:
                    messages.error(request, f"Representante con RUT '{representante_rut}' no encontrado.")
                    continue

                # Crear el estudiante con curso actual y representante
                student = Student.objects.create(
                    rut=rut,
                    nombres=nombres,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    sexo=sexo,
                    fecha_nacimiento=fecha_nacimiento,
                    fecha_admision=fecha_admision,
                    telefono_apoderado=telefono_apoderado,
                    direccion=direccion,
                    observaciones=observaciones,
                    email=email,
                    estado="activo",
                    curso_actual=curso,
                    representante=representante
                )

                # Asignar la asignatura al estudiante
                student.subjects.add(subject)

                # Generar contraseña y crear usuario en auth_user
                password = generate_random_password()
                user = User.objects.create_user(
                    username=rut,
                    password=password,
                    first_name=nombres,
                    last_name=f"{apellido_paterno} {apellido_materno}",
                    email=email,
                )

                # Asignar grupo "Alumno" al usuario
                alumno_group = Group.objects.get(name="Alumno")
                user.groups.add(alumno_group)

                # Enviar contraseña por correo electrónico
                send_mail(
                    "Tu cuenta ha sido creada",
                    f"Tu usuario es {rut} y tu contraseña es: {password}",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

            messages.success(request, "Estudiantes subidos y cuentas creadas exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")
        return redirect("upload-student-excel")
    return render(request, "students/students_upload.html")

def generate_random_password(length=8):
    import random
    import string
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def generate_student_excel_template(request):
    columns = [
        "rut", "apellido_paterno", "apellido_materno", "nombres",
        "sexo", "fecha_nacimiento", "fecha_admision", "curso_actual", "asignatura",
        "representante", "telefono_apoderado", "direccion", "observaciones", "email"
    ]
    # Crear DataFrame vacío con las columnas
    df = pd.DataFrame(columns=columns)

    # Guardar en un archivo de Excel en memoria
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=plantilla_estudiantes.xlsx"
    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Estudiantes")
    
    return response



class StudentSubjectsListView(ListView):
    model = Subject
    template_name = 'students/student_subjects.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        student_id = self.kwargs['pk']
        student = get_object_or_404(Student, pk=student_id)
        return student.subjects.all() 
    
class SubjectDetailView(DetailView):
    model = Subject
    template_name = 'students/student_subjects_detail.html'
    context_object_name = 'subject'


class EventListView(ListView):
    model = Event
    template_name = "students/student_calendar.html"
    context_object_name = "events"


    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            subject_id = self.kwargs.get("subject_id")
            events = Event.objects.filter(subject_id=subject_id)
            out = [
                {
                    'title': event.title,
                    'id': event.id,
                    'start': event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    'end': event.end_time.strftime("%Y-%m-%dT%H:%M:%S") if event.end_time else event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                for event in events
            ]
            return JsonResponse(out, safe=False)
        return super().get(request, *args, **kwargs)
    

class AnnouncementListView(ListView):
    model = Announcement
    template_name = "students/student_announcements.html"
    context_object_name = "announcements"

    def get_queryset(self):
        # Filtra los anuncios por `subject_id` obtenido de la URL
        subject_id = self.kwargs.get("subject_id")
        return Announcement.objects.filter(subject_id=subject_id)
    


