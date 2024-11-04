from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View

from apps.corecode.models import Subject
from apps.students.models import Student

from .models import Result


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
        return redirect('subject_detail', subject_id=subject.id)

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