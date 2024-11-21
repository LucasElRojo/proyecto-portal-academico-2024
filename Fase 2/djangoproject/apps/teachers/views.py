import random
import string
from django import forms
from django.http import JsonResponse
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

import json
from django.utils.dateparse import parse_datetime, parse_date

from apps.corecode.models import Attendance, Subject
from apps.result.models import Result
from apps.students.models import Student
from apps.teachers.forms import AnnotationFilterForm, AnnotationForm, TeacherAnnotationForm

from .models import Annotation, ClassRecord, Teacher, Event
from apps.corecode.models import Announcement


from django.utils.decorators import method_decorator
from apps.corecode.decorators import  teacher_required, teacher_or_staff_required, staff_or_superuser_required
from django.utils import timezone

@method_decorator(staff_or_superuser_required, name='dispatch')
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

@method_decorator(teacher_required, name='dispatch')
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
    

@method_decorator(teacher_required, name='dispatch')
class EventListView(ListView):
    model = Event
    template_name = "teachers/teacher_calendar.html"
    context_object_name = "events"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_profesor'] = self.request.user.groups.filter(name='profesor').exists()
        return context

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

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            title = data.get('title')
            start_time = parse_datetime(data.get('start'))
            end_time = parse_datetime(data.get('end'))
            subject_id = self.kwargs.get("subject_id")

            if not title or not start_time:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El título y la fecha de inicio son obligatorios.'
                }, status=400)

            event = Event.objects.create(
                title=title,
                start_time=start_time,
                end_time=end_time,
                subject_id=subject_id
            )

            return JsonResponse({
                'status': 'success',
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'start': event.start_time.isoformat(),
                    'end': event.end_time.isoformat() if event.end_time else event.start_time.isoformat(),
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Error en el formato JSON.'}, status=400)
        except Exception as e:
            print("Error al crear evento:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


    def delete(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            event_id = data.get("id")

            if not event_id:
                return JsonResponse({"status": "error", "message": "Falta el ID del evento."}, status=400)

            event = Event.objects.get(id=event_id)
            event.delete()
            return JsonResponse({"status": "success"})
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "El evento no existe."}, status=404)
        except Exception as e:
            print("Error al eliminar evento:", e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        



class TeacherAnnouncementListView(ListView):
    model = Announcement
    template_name = "teachers/teacher_announcement_list.html"
    context_object_name = "announcements"

    def get_queryset(self):
        # Obtener el ID de la asignatura de la URL
        subject_id = self.kwargs.get("subject_id")
        # Obtener el usuario actual y buscar al profesor 
        user = self.request.user
           
        teacher = get_object_or_404(Teacher, email=user.email)  

        # Verificar que el profesor esté asociado con la asignatura específica
        subject = get_object_or_404(teacher.subjects, id=subject_id)  

        # Filtrar los anuncios por tipo de usuario, asignatura y ordenarlos por fecha
        return Announcement.objects.filter(
            target_user_type='teacher',
            subject=subject
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        # Añadir la asignatura al contexto para mostrar su nombre en el template
        context = super().get_context_data(**kwargs)
        context['subject'] = get_object_or_404(Subject, id=self.kwargs.get("subject_id"))
        return context

@method_decorator(teacher_required, name='dispatch')
class TeacherAnnouncementCreateView(CreateView):
    model = Announcement
    template_name = "teachers/teacher_announcement_form.html"
    fields = ['title', 'content']
    
    def form_valid(self, form):
        # Obtener el subject desde la URL y asignarlo al anuncio
        subject_id = self.kwargs.get("subject_id")
        teacher = get_object_or_404(Teacher, email=self.request.user.email)  
        subject = get_object_or_404(teacher.subjects, id=subject_id)

        form.instance.target_user_type = 'teacher'
        form.instance.subject = subject  # Asigna la asignatura al anuncio
        return super().form_valid(form)

    def get_success_url(self):
        # Redirige de nuevo a la lista de anuncios de esta asignatura
        return reverse_lazy('teacher_announcements', kwargs={'subject_id': self.kwargs.get("subject_id")})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject'] = get_object_or_404(Subject, id=self.kwargs.get("subject_id"))  # Asegura que el contexto tenga 'subject'
        return context
    
    
# Seccion de notas

def teacher_subject_list(request):
    # Obtener al profesor autenticado basado en el username y rut
    try:
        teacher = Teacher.objects.get(rut=request.user.username)
    except Teacher.DoesNotExist:
        messages.error(request, "No se encontró al profesor asociado al usuario.")
        return redirect('home')  # Redirige a la página principal o al login

    # Obtener las asignaturas del profesor
    subjects = teacher.subjects.all()
    return render(request, 'teachers/teacher_subject_list.html', {'subjects': subjects})

def teacher_create_result(request, subject_id):
    try:
        teacher = Teacher.objects.get(rut=request.user.username)
    except Teacher.DoesNotExist:
        messages.error(request, "No se encontró al profesor asociado al usuario.")
        return redirect('home')

    subject = get_object_or_404(Subject, id=subject_id)

    # Verificar que el profesor está asignado a la asignatura
    if subject not in teacher.subjects.all():
        messages.error(request, "No tienes permiso para acceder a esta asignatura.")
        return redirect('teacher_subject_list')

    students = Student.objects.filter(subjects=subject)
    n_scores = 5  # Número de notas
    n_range = range(1, n_scores + 1)

    # Obtener resultados existentes
    results = Result.objects.filter(subject=subject, student__in=students)
    results_dict = {f'{result.student.id}_{result.n_score}': result.score for result in results}

    if request.method == 'POST':
        for student in students:
            for n in n_range:
                score_value = request.POST.get(f'score_{student.id}_{n}')
                if score_value:
                    # Normalizar la nota al rango permitido
                    score_value = float(score_value)
                    if score_value > 7.0 or score_value < 1.0:  # Si no está en el rango [1.0, 7.0]
                        score_value = normalize_score(score_value)

                    Result.objects.update_or_create(
                        student=student,
                        subject=subject,
                        n_score=n,
                        defaults={'score': score_value, 'current_class': student.curso_actual}
                    )
                else:
                    Result.objects.filter(student=student, subject=subject, n_score=n).delete()
        messages.success(request, 'Notas guardadas exitosamente.')
        return redirect('teacher_create_result', subject_id=subject.id)

    context = {
        'subject': subject,
        'students': students,
        'results_dict': results_dict,
        'n_range': n_range,
    }
    return render(request, 'teachers/teacher_add_results.html', context)

def normalize_score(score_value):
    """
    Normaliza una nota al rango permitido [1.0, 7.0].
    """
    score_str = str(int(score_value))  # Asegura que sea entero para manipularlo como string
    if len(score_str) > 1:
        # Inserta el punto decimal entre los dos últimos dígitos
        normalized = float(score_str[:-1] + '.' + score_str[-1])
    else:
        # Si es un solo dígito, lo interpreta como una nota válida
        normalized = float(score_str + '.0')

    # Asegura que esté dentro del rango permitido
    return min(max(normalized, 1.0), 7.0)


def teacher_subject_list_get(request):
    """
    Lista las asignaturas asociadas al profesor autenticado.
    """
    teacher = get_object_or_404(Teacher, rut=request.user.username)  # Basado en el RUT (username)
    subjects = teacher.subjects.all()  # Asignaturas asignadas al profesor

    context = {
        'subjects': subjects,
        'current_date': timezone.now()
    }
    return render(request, 'teachers/teacher_subject_attendance.html', context)

def attendance_register(request, subject_id):
    """
    Registra una nueva clase y permite registrar la asistencia de los estudiantes.
    """
    teacher = get_object_or_404(Teacher, rut=request.user.username)
    subject = get_object_or_404(Subject, id=subject_id)

    # Verificar que el profesor está asignado a la asignatura
    if subject not in teacher.subjects.all():
        messages.error(request, "No tienes permiso para registrar una clase en esta asignatura.")
        return redirect('teacher_subject_list')

    students = Student.objects.filter(subjects=subject)

    if request.method == 'POST':
        # Crear un nuevo registro de clase
        class_record = ClassRecord.objects.create(
            subject=subject,
            teacher=teacher,
            description=request.POST.get('description', ''),
        )

        # Registrar la asistencia de los estudiantes
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'ausente')
            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                class_record=class_record,
                defaults={'status': status}
            )

        messages.success(request, "Clase y asistencia registradas exitosamente.")
        return redirect('teacher_subject_list')

    context = {
        'subject': subject,
        'students': students,
        'current_date': timezone.now(),
    }
    return render(request, 'teachers/teacher_attendance_register.html', context)