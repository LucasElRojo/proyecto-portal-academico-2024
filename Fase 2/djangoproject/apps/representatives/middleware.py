from .models import Representatives  

class RepresentativesID:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                representative = Representatives.objects.get(rut=request.user.username)  
                request.session['Representatives_id'] = representative.id
            except Representatives.DoesNotExist:
                request.session['Representatives_id'] = None 
        return self.get_response(request)
