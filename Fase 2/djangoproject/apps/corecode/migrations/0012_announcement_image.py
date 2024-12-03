# Generated by Django 4.2.7 on 2024-12-02 23:25

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("corecode", "0011_alter_attendance_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="announcement",
            name="image",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True, verbose_name="image"
            ),
        ),
    ]