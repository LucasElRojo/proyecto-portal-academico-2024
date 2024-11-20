from rest_framework import serializers
from .models import CarouselItem

class CarouselItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CarouselItem
        fields = ['id', 'title', 'image_url', 'image_file', 'description', 'image']

    def get_image(self, obj):
        """
        Devuelve la URL de la imagen a mostrar en el carrusel.
        """
        return obj.get_image()