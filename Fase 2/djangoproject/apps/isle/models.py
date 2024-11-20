from django.db import models

# Create your models here.

class CarouselItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ImageField(upload_to='carousel_images/', blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_image(self):
        """
        Devuelve la URL de la imagen. Prioriza `image_file` si existe,
        de lo contrario usa `image_url`.
        """
        if self.image_file:
            return self.image_file.url
        return self.image_url