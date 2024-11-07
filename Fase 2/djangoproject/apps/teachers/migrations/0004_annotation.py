# Generated by Django 4.2.7 on 2024-11-03 05:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("corecode", "0008_alter_subject_name"),
        ("students", "0008_student_subjects"),
        ("teachers", "0003_teacher_subjects_alter_teacher_foto"),
    ]

    operations = [
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
                        choices=[("positive", "Positive"), ("negative", "Negative")],
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