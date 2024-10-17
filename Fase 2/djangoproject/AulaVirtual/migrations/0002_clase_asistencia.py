# Generated by Django 4.2 on 2024-10-17 01:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AulaVirtual', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clases', to='AulaVirtual.curso')),
            ],
        ),
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('S', 'Presente'), ('N', 'Ausente'), ('J', 'Justificado')], max_length=1)),
                ('alumno', models.ForeignKey(limit_choices_to={'tipo_usuario__tipo': 'Alumno'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('clase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asistencias', to='AulaVirtual.clase')),
            ],
            options={
                'unique_together': {('alumno', 'fecha', 'clase')},
            },
        ),
    ]
