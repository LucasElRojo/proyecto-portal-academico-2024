from django.db import models

from apps.corecode.models import (
    AcademicSession,
    AcademicTerm,
    StudentClass,
    Subject,
)
from apps.students.models import Student

from .utils import score_grade


# Create your models here.
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    current_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    n_score = models.PositiveIntegerField(null=True)
    average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ["subject"]

    def __str__(self):
        return f"{self.student} {self.subject}"
