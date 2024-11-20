from django import template
from apps.representatives.models import Representatives
from apps.students.models import Student

register = template.Library()

@register.simple_tag(takes_context=True)
def get_hijos(context):
    user = context['user']
    try:
        # El username y el RUT son iguales, busca el representante
        representante = Representatives.objects.get(rut=user.username)
        # Devuelve todos los hijos asociados al representante
        return representante.get_estudiantes()
    except Representatives.DoesNotExist:
        return None

@register.simple_tag(takes_context=True)
def get_representative_id(context):
    user = context['user']
    if user.is_authenticated:
        try:
            representative = Representatives.objects.get(rut=user.username)
            return representative.id
        except Representatives.DoesNotExist:
            return None
    return None

@register.simple_tag(takes_context=True)
def get_student_id(context, student_rut):
    try:
        student = Student.objects.get(rut=student_rut)
        return student.id
    except Student.DoesNotExist:
        return None