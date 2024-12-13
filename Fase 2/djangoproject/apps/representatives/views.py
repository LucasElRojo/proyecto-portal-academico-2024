from django.utils import timezone
import random
import string

from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.utils.dateparse import parse_datetime, parse_date
from django.http import JsonResponse

from apps.finance.models import Invoice, InvoiceItem, Receipt
from apps.result.models import Result

from .models import Representatives
from apps.students.models import Student
from apps.students.models import Subject
from apps.teachers.models import Event, Annotation
from apps.corecode.models import Announcement

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
import logging

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
    success_url = reverse_lazy("representatives-list")
    
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
    

class EventListView(ListView):
    model = Event
    template_name = "representatives/representatives_calendar.html"
    context_object_name = "events"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todas las asignaturas disponibles para el filtro
        context['subjects'] = Subject.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            subject_id = request.GET.get("subject_id")
            
            # Filtrar eventos por asignatura si se proporciona un subject_id
            events = Event.objects.all()
            if subject_id:
                events = events.filter(subject_id=subject_id)
            
            # Convertir los eventos a un formato JSON compatible con FullCalendar
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
        
        # Carga de página normal
        return super().get(request, *args, **kwargs)
    



class RepresentativeAnnotationsView(ListView):
    model = Annotation
    template_name = "representatives/representatives_annotation_student.html"
    context_object_name = "annotations"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el representative
        representative_id = self.kwargs.get('representative_id')
        representative = get_object_or_404(Representatives, id=representative_id)
        context['representative'] = representative

        # Obtener el estudiante específico del representative
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(Student, id=student_id, representante=representative)
        context['student'] = student

        # Obtener todas las asignaturas del estudiante (para el filtro)
        subjects = Subject.objects.filter(students=student).distinct()
        context['subjects'] = subjects

        # Filtrar las anotaciones del estudiante por asignatura (subject_id)
        subject_id = self.request.GET.get("subject_id")
        if subject_id:
            context['selected_subject'] = Subject.objects.get(id=subject_id)
            context['annotations'] = Annotation.objects.filter(student=student, subject_id=subject_id)
        else:
            context['selected_subject'] = None
            context['annotations'] = Annotation.objects.filter(student=student)

        return context
    


class RepresentativeAnnouncementListView(ListView):
    model = Announcement
    template_name = "representatives/representatives_announcements.html"
    context_object_name = "announcements"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el representative
        representative_id = self.kwargs.get('representative_id')
        representative = get_object_or_404(Representatives, id=representative_id)
        context['representative'] = representative

        # Obtener el estudiante específico del representative
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(Student, id=student_id, representante=representative)
        context['student'] = student

        # Obtener todas las asignaturas del estudiante (para el filtro)
        subjects = Subject.objects.filter(students=student).distinct()
        context['subjects'] = subjects

        # Filtrar los anuncios del estudiante por asignatura (`subject_id`)
        subject_id = self.request.GET.get("subject_id")
        if subject_id:
            context['selected_subject'] = Subject.objects.get(id=subject_id)
            context['announcements'] = Announcement.objects.filter(subject_id=subject_id)
        else:
            context['selected_subject'] = None
            context['announcements'] = Announcement.objects.filter(subject__students=student)

        return context

def student_grades_view(request, student_id):
    # Obtener al estudiante
    student = get_object_or_404(Student, id=student_id)

    # Obtener todas las asignaturas del estudiante
    subjects = student.subjects.all()

    # Filtrar por asignatura si el parámetro `subject_id` está en la solicitud
    subject_id = request.GET.get('subject_id')
    selected_subject = None
    if subject_id:
        selected_subject = get_object_or_404(Subject, id=subject_id)
        subjects = [selected_subject]

    # Preparar las calificaciones del estudiante por asignatura
    grades_data = []
    for subject in subjects:
        results = Result.objects.filter(student=student, subject=subject).order_by('n_score')

        # Obtener las notas y calcular el promedio
        scores = [result.score for result in results]
        average = (
            sum(score for score in scores if score is not None) / len(scores)
            if len(scores) > 0 and any(scores)
            else None
        )

        grades_data.append({
            'subject': subject,
            'scores': scores,
            'average': average,
        })

    # Rango de notas (asume 5 columnas para las notas)
    max_scores = 5
    for grade in grades_data:
        grade['scores'] += [None] * (max_scores - len(grade['scores']))  # Rellenar con None si faltan notas

    # Contexto para la plantilla
    context = {
        'student': student,
        'grades_data': grades_data,
        'subjects': Subject.objects.all(),
        'selected_subject': selected_subject,
        'n_range': range(1, max_scores + 1),
    }
    return render(request, 'representatives/representatives_student_grades.html', context)


# Webpay :DDD

@login_required
def student_payment_history(request, student_id):
    invoice = get_object_or_404(Invoice, student__id=student_id)
    items = InvoiceItem.objects.filter(invoice=invoice)
    receipts = Receipt.objects.filter(invoice=invoice)
    context = {
        'object': invoice,
        'items': items,
        'receipts': receipts,
    }
    return render(request, 'representatives/representatives_payment_history.html', context)


@login_required
def make_payment(request, item_id):
    item = get_object_or_404(InvoiceItem, id=item_id)
    # Aquí se realizaría el proceso de pago con kiphu o alguna wea asi xD
    # Crear un nuevo recibo de pago asociado al item
    Receipt.objects.create(
        invoice=item.invoice,
        item=item,
        amount_paid=item.amount,
        date_paid=timezone.now(),
        comment="Pago realizado"
    )
    return redirect(reverse('student-payment-history', args=[item.invoice.student.id]))

# Configurar el logger
logger = logging.getLogger(__name__)

def make_multiple_payments(request):
    if request.method == "POST":
        selected_items_ids = request.POST.getlist('selected_items')
        selected_total = request.POST.get("selected_total")

        # Validar monto total
        print(f"Valor: {selected_total}, Tipo: {type(selected_total)}")
        try:
            total_selected = float(selected_total)
            if total_selected <= 0:
                raise ValueError("El monto debe ser mayor a cero.")
        except (ValueError, TypeError):
            logger.error("Monto inválido para la transacción.")
            return render(request, "representatives/payment_error.html", {"message": "Monto inválido."})

        # Registrar los pagos individuales
        for item_id in selected_items_ids:
            try:
                item = InvoiceItem.objects.get(id=item_id)
                Receipt.objects.create(
                    invoice=item.invoice,
                    item=item,
                    amount_paid=item.amount,
                    date_paid=timezone.now(),
                    comment="Pago realizado"
                )
                logger.info(f"Pago registrado para el item {item_id}")
            except InvoiceItem.DoesNotExist:
                logger.warning(f"Item con ID {item_id} no encontrado. Saltando.")
            except Exception as e:
                logger.error(f"Error al registrar el pago para el item {item_id}: {e}")

        # Iniciar la transacción con Webpay
        transaction = Transaction()
        transaction.commerce_code = settings.WEBPAY_COMMERCE_CODE
        transaction.api_key = settings.WEBPAY_API_KEY
        transaction.integration_type = IntegrationType.TEST

        buy_order = f"orden-{random.randint(1000, 9999)}"
        session_id = str(request.user.id)
        return_url = request.build_absolute_uri(reverse("webpay-confirm-payment"))

        try:
            response = transaction.create(buy_order, session_id, int(total_selected), return_url)
            logger.info(f"Transacción iniciada con éxito. Monto: {total_selected}, Orden: {buy_order}")
            return redirect(f"{response['url']}?token_ws={response['token']}")
        except Exception as e:
            logger.error(f"Error al iniciar la transacción: {e}")
            return render(request, "representatives/payment_error.html", {"message": f"Error al iniciar el pago: {e}"})

    return redirect("student-payment-history")

            

def confirm_payment(request):
    token = request.POST.get("token_ws") or request.GET.get("token_ws")
    if not token:
        return render(request, "representatives/payment_error.html", {"message": "Token no recibido."})

    transaction = Transaction()
    transaction.commerce_code = settings.WEBPAY_COMMERCE_CODE
    transaction.api_key = settings.WEBPAY_API_KEY
    transaction.integration_type = IntegrationType.LIVE

    try:
        response = transaction.commit(token)
        if response.get("status") == "AUTHORIZED":
            # Registra el pago exitoso
            return render(request, "representatives/payment_success.html", {"response": response})
        else:
            return render(request, "representatives/payment_error.html", {"message": "El pago no fue autorizado."})
    except Exception as e:
        return render(request, "representatives/payment_error.html", {"message": f"Error al confirmar el pago: {e}"})



def dashboard(request):
    # Lógica de la vista
    return render(request, 'representatives/dashboard.html')