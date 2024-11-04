from .models import Teacher

class TeacherID:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                teacher = Teacher.objects.get(rut=request.user.username)
                request.session['teacher_id'] = teacher.id
            except Teacher.DoesNotExist:
                request.session['teacher_id'] = None 
        return self.get_response(request)
