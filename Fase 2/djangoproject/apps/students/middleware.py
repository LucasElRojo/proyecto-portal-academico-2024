from .models import Student

class StudentID:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                student = Student.objects.get(rut=request.user.username)
                request.session['student_id'] = student.id
            except Student.DoesNotExist:
                request.session['student_id'] = None 
        return self.get_response(request)
