from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import modelformset_factory


class UserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['rut','password','primer_nombre','segundo_nombre','primer_apellido', 'segundo_apellido', 'email', 'telefono', 'tipo_usuario']

class LoginForm(forms.Form):
    rut = forms.CharField(max_length=12)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        rut = self.cleaned_data.get('rut')
        password = self.cleaned_data.get('password')

        if rut and password:
            user = authenticate(rut=rut, password=password)
            if not user:
                raise forms.ValidationError("RUT o contraseña incorrectos.")
        return super().clean()
    
class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['rut', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'email', 'telefono']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password_confirm

    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(widget=forms.PasswordInput)
    nueva_password = forms.CharField(widget=forms.PasswordInput)
    confirmar_nueva_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password_actual(self):
        password_actual = self.cleaned_data.get('password_actual')
        if not self.user.check_password(password_actual):
            raise forms.ValidationError("La contraseña actual es incorrecta.")
        return password_actual

    def clean_confirmar_nueva_password(self):
        nueva_password = self.cleaned_data.get('nueva_password')
        confirmar_nueva_password = self.cleaned_data.get('confirmar_nueva_password')
        if nueva_password != confirmar_nueva_password:
            raise forms.ValidationError("Las contraseñas nuevas no coinciden.")
        return confirmar_nueva_password
    
    
class RecuperarPasswordForm(forms.Form):
    rut = forms.CharField(max_length=12)
    nueva_password = forms.CharField(widget=forms.PasswordInput)
    confirmar_nueva_password = forms.CharField(widget=forms.PasswordInput)

    def clean_confirmar_nueva_password(self):
        nueva_password = self.cleaned_data.get('nueva_password')
        confirmar_nueva_password = self.cleaned_data.get('confirmar_nueva_password')
        if nueva_password != confirmar_nueva_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return confirmar_nueva_password
    


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'profesor', 'fecha_inicio', 'fecha_fin']

    # Filtrar los profesores en el dropdown
    def __init__(self, *args, **kwargs):
        super(CursoForm, self).__init__(*args, **kwargs)
        # Limitar las opciones del campo 'profesor' solo a usuarios con tipo 'Profesor'
        self.fields['profesor'].queryset = Usuario.objects.filter(tipo_usuario__tipo='Profesor')


class RecursoForm(forms.ModelForm):
    class Meta:
        model = Recurso
        fields = ['descripcion', 'archivo']

class AnotacionForm(forms.ModelForm):
    class Meta:
        model = Anotacion
        fields = ['comentario', 'positiva']

class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = ['titulo',  'comentarios', 'archivo']



class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['valor'] 
        widgets = {
            'valor': forms.NumberInput(attrs={'step': '0.1', 'min': '1', 'max': '10', 'class': 'form-control'})
        }


# Profe Asistencia
class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = ['fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

class AsistenciaForm(forms.Form):
    ESTADO_ASISTENCIA = Asistencia.ESTADO_ASISTENCIA

    def __init__(self, *args, **kwargs):
        alumnos = kwargs.pop('alumnos')
        super().__init__(*args, **kwargs)
        self.alumno_field_pairs = []
        for alumno in alumnos:
            field_name = f'estado_{alumno.id}'
            self.fields[field_name] = forms.ChoiceField(
                choices=self.ESTADO_ASISTENCIA,
                widget=forms.RadioSelect(attrs={'class': 'd-inline-block'}),
                label=''
            )
            self.alumno_field_pairs.append((alumno, self[field_name]))
            
#Formulario pal email uwu
class EmailForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=True)
    
    class Meta:
        model = Emails
        exclude = ['created_at', 'edited_at', 'message', 'subject']
        

class AsignarCursoForm(forms.Form):
    profesor = forms.ModelChoiceField(queryset=Usuario.objects.filter(tipo_usuario__tipo='Profesor'))
    curso = forms.ModelChoiceField(queryset=Curso.objects.all())


class UnidadForm(forms.ModelForm):
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), empty_label="Seleccionar Curso")

    class Meta:
        model = Unidad
        fields = ['nombre', 'curso']