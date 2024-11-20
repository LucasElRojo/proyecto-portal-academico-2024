# Generated by Django 4.2.7 on 2024-11-20 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("isle", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="carouselitem",
            name="image_file",
            field=models.ImageField(
                blank=True, null=True, upload_to="carousel_images/"
            ),
        ),
        migrations.AlterField(
            model_name="carouselitem",
            name="image_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
