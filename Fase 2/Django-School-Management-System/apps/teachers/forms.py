# apps/teachers/forms.py
from django import forms
from apps.students.models import Student
from .models import Annotation, Teacher

class AnnotationFilterForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False, label="Student")
    annotation_type = forms.ChoiceField(choices=Annotation.ANNOTATION_TYPE_CHOICES, required=False, label="Type")

class AnnotationForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        label="Profesor",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Annotation
        fields = ['student', 'teacher', 'subject', 'annotation_type', 'comment']
        labels = {
            'student': 'Alumno',
            'subject': 'Asignatura',
            'annotation_type': 'Tipo de Anotación',
            'comment': 'Comentario',
        }
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'annotation_type': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }
        

class TeacherAnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ['student', 'annotation_type', 'comment']
        labels = {
            'student': 'Alumno',
            'annotation_type': 'Tipo de Anotación',
            'comment': 'Comentario',
        }
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'annotation_type': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }