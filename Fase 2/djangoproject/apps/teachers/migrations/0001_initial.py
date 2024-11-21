# Generated by Django 4.2.7 on 2024-11-21 04:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("students", "0008_student_subjects"),
        ("corecode", "0010_alter_announcement_content"),
    ]

    operations = [
        migrations.CreateModel(
            name="Teacher",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rut",
                    models.CharField(
                        blank=True,
                        max_length=12,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="El RUT debe estar en el formato 'XXXXXXXX-X'",
                                regex="^\\d{1,2}\\d{3}\\d{3}-[0-9kK]{1}$",
                            )
                        ],
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[("activo", "Activo"), ("inactivo", "Inactivo")],
                        default="activo",
                        max_length=10,
                    ),
                ),
                ("apellido_paterno", models.CharField(max_length=200)),
                ("apellido_materno", models.CharField(max_length=200)),
                ("nombres", models.CharField(blank=True, max_length=200)),
                (
                    "sexo",
                    models.CharField(
                        choices=[("masculino", "Masculino"), ("femenino", "Femenino")],
                        default="masculino",
                        max_length=10,
                    ),
                ),
                (
                    "fecha_nacimiento",
                    models.DateField(default=django.utils.timezone.now),
                ),
                ("fecha_admision", models.DateField(default=django.utils.timezone.now)),
                (
                    "telefono",
                    models.CharField(
                        blank=True,
                        max_length=15,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="El número de teléfono no tiene el formato correcto.",
                                regex="^[0-9]{9,15}$",
                            )
                        ],
                    ),
                ),
                ("direccion", models.TextField(blank=True)),
                ("observaciones", models.TextField(blank=True)),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        unique=True,
                        validators=[django.core.validators.EmailValidator()],
                    ),
                ),
                ("foto", models.ImageField(blank=True, upload_to="students/fotos/")),
                (
                    "subjects",
                    models.ManyToManyField(
                        blank=True, related_name="teachers", to="corecode.subject"
                    ),
                ),
            ],
            options={
                "ordering": ["apellido_paterno", "apellido_materno", "nombres"],
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                (
                    "subject",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="corecode.subject",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ClassRecord",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="corecode.subject",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="teachers.teacher",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="Annotation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "annotation_type",
                    models.CharField(
                        choices=[("positiva", "Positiva"), ("negativa", "Negativa")],
                        max_length=10,
                    ),
                ),
                ("comment", models.TextField()),
                ("date", models.DateField(default=django.utils.timezone.now)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="annotations",
                        to="students.student",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="annotations",
                        to="corecode.subject",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="annotations",
                        to="teachers.teacher",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
    ]
