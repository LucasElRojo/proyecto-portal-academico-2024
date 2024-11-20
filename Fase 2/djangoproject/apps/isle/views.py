from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import render
from .models import CarouselItem
from .serializers import CarouselItemSerializer

from apps.representatives.models import Representatives
from apps.students.models import Student

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

def carousel_view(request):
    return render(request, 'isle/index.html')

def carousel_Form_view(request):
    return render(request, 'isle/form.html')

def carousel_update_delete(request):
    return render(request, 'isle/list.html')

def carousel_update(request, pk):
    return render(request, 'isle/update.html')

class CarouselItemList(generics.ListCreateAPIView):
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        # Crear un nuevo CarouselItem basado en la imagen local o la URL
        image_file = request.FILES.get('image_file')
        image_url = data.get('image_url')

        if not image_file and not image_url:
            return Response(
                {"error": "Debes proporcionar una URL o subir una imagen."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        carousel_item = CarouselItem(
            title=data.get('title'),
            description=data.get('description'),
            image_url=image_url,
            image_file=image_file,
        )
        carousel_item.save()

        return Response(CarouselItemSerializer(carousel_item).data, status=status.HTTP_201_CREATED)


class CarouselItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer
    lookup_field = 'pk'  # Use 'id' as the lookup field



class RepresentativeDashboardView(TemplateView):
    template_name = "isle/representatives_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el representante desde la sesión
        representative_id = self.request.session.get('Representatives_id')
        if not representative_id:
            raise ValueError("No se encontró el 'Representatives_id' en la sesión.")

        representative = get_object_or_404(Representatives, id=representative_id)
        context['representative'] = representative

        # Obtener todos los estudiantes asociados al representante
        students = Student.objects.filter(representante=representative)

        if students.exists():
            # Selecciona un estudiante específico si está en los parámetros GET
            student_id = self.request.GET.get('student_id')
            if student_id:
                student = get_object_or_404(students, id=student_id)
            else:
                student = students.first()  # Selecciona el primer estudiante por defecto

            context['student'] = student
            context['students'] = students
        else:
            # No hay estudiantes asignados
            context['students'] = []
            context['student'] = None

        return context
