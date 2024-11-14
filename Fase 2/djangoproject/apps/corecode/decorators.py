from django.core.exceptions import PermissionDenied
from functools import wraps
from apps.teachers.models import Teacher
from apps.staffs.models import Staff
from apps.students.models import Student
from django.shortcuts import redirect


def teacher_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            # Verifica si el usuario tiene un registro en el modelo Teacher
            teacher = Teacher.objects.get(email=request.user.email)  # Suponiendo que el email es único
            if teacher:
                return function(request, *args, **kwargs)
        except Teacher.DoesNotExist:
            return redirect('home')  # Redirige al home si el usuario no es un teacher
    return wrap

def staff_or_superuser_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            if request.user.is_superuser or Staff.objects.filter(email=request.user.email).exists():
                return function(request, *args, **kwargs)
            else:
                return redirect('home')
        except Staff.DoesNotExist:
            return redirect('home') 
    return wrap


def teacher_or_staff_required(function):
    """Permitir acceso si el usuario es staff o teacher"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if Teacher.objects.filter(email=request.user.email).exists() or \
           Staff.objects.filter(email=request.user.email).exists():
            return function(request, *args, **kwargs)
        return redirect('home')  # Redirige al home si el usuario no es ni teacher ni staff
    return wrap