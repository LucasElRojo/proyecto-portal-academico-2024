from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View

from apps.corecode.models import Subject
from apps.students.models import Student

from .models import Result
from django.db.models import Avg



@login_required
def create_result(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    students = Student.objects.filter(subjects=subject)
    n_scores = 5  # Número de notas
    n_range = range(1, n_scores + 1)

    # Obtener resultados existentes
    results = Result.objects.filter(subject=subject, student__in=students)
    results_dict = {}
    for result in results:
        key = f'{result.student.id}_{result.n_score}'
        results_dict[key] = result.score

    if request.method == 'POST':
        for student in students:
            for n in n_range:
                score_value = request.POST.get(f'score_{student.id}_{n}')
                if score_value:
                    score_value = float(score_value)
                    Result.objects.update_or_create(
                        student=student,
                        subject=subject,
                        n_score=n,
                        defaults={'score': score_value, 'current_class': student.curso_actual}
                    )
                else:
                    # Eliminar resultado si el campo está vacío
                    Result.objects.filter(student=student, subject=subject, n_score=n).delete()
        messages.success(request, 'Notas guardadas exitosamente.')
        return redirect('subject_list')

    context = {
        'subject': subject,
        'students': students,
        'results_dict': results_dict,
        'n_range': n_range,
    }
    return render(request, 'result/add_results.html', context)
    
@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    return render(request, 'result/subject_detail.html', {'subject': subject})

@login_required
def edit_results(request):
    return render(request, "result/edit_results.html")


class ResultListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Filtra los resultados de la sesión y el término actual
        results = Result.objects.filter(
            session=request.current_session, term=request.current_term
        )
        
        bulk = {}

        # Procesa cada resultado
        for result in results:
            subjects = []
            score_total = 0
            for subject_result in results:
                # Verifica si el resultado corresponde al mismo estudiante
                if subject_result.student == result.student:
                    subjects.append(subject_result)
                    
                    # Suma todas las calificaciones para cada materia
                    score_total += (
                        subject_result.score_1 + 
                        subject_result.score_2 + 
                        subject_result.score_3 + 
                        subject_result.score_4
                    )

            # Calcula el promedio en base a 4 calificaciones
            average_score = score_total / (len(subjects) * 4) if subjects else 0
            
            # Asigna datos al diccionario para el estudiante
            bulk[result.student.id] = {
                "student": result.student,
                "subjects": subjects,
                "score_total": score_total,  # Suma de todas las calificaciones
                "average_score": average_score  # Promedio
            }

        context = {"results": bulk}
        return render(request, "result/all_results.html", context)

def subject_list(request):
    subjects = Subject.objects.prefetch_related('teachers').all()
    return render(request, 'result/subject_list.html', {'subjects': subjects})






class ResultViews(ListView):
    template_name = "result/view_result.html"
    context_object_name = "student_results"

    def get_queryset(self):
        return []  # ListView espera un queryset, pero no lo usamos aquí

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todas las asignaturas
        subjects = Subject.objects.all()
        context['subjects'] = subjects

        # Filtrar por asignatura si `subject_id` está presente en los parámetros GET
        subject_id = self.request.GET.get('subject_id')
        if subject_id:
            selected_subject = get_object_or_404(Subject, id=subject_id)
            context['selected_subject'] = selected_subject
        else:
            selected_subject = None
            context['selected_subject'] = None

        # Procesar resultados de los estudiantes
        students = Student.objects.all()

        # Si hay un subject seleccionado, filtrar los estudiantes inscritos en ese subject
        if selected_subject:
            students = students.filter(subjects=selected_subject)

        student_results = []

        for student in students:
            student_data = {
                "student": student,
                "subjects": [],
            }

            # Filtrar asignaturas según el filtro seleccionado
            filtered_subjects = [selected_subject] if selected_subject else subjects

            for subject in filtered_subjects:
                # Validar que el estudiante esté inscrito en la asignatura
                if subject not in student.subjects.all():
                    continue  # Saltar si el estudiante no está inscrito en esta asignatura

                results = Result.objects.filter(student=student, subject=subject).order_by("n_score")

                # Verifica si hay resultados y calcula el promedio
                if results.exists():
                    total_score = sum(result.score for result in results if result.score is not None)
                    count_scores = results.filter(score__isnull=False).count()
                    average = total_score / count_scores if count_scores > 0 else None
                    subject_data = {
                        "subject": subject,
                        "scores": [result.score for result in results],  # Todas las notas
                        "average": average,
                    }
                else:
                    subject_data = {
                        "subject": subject,
                        "scores": [None] * 5,  # Asume 5 notas por asignatura si no hay datos
                        "average": None,
                    }

                student_data["subjects"].append(subject_data)

            if student_data["subjects"]:  # Solo agregar estudiantes con asignaturas válidas
                student_results.append(student_data)

        context['student_results'] = student_results
        context['n_range'] = range(1, 6)  # Suponiendo que hay 5 notas
        return context


