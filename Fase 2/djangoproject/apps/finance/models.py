from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from apps.students.models import Student


class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Estudiante")
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, verbose_name="Año")
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, verbose_name="Semestre")
    class_for = models.ForeignKey(StudentClass, on_delete=models.CASCADE, verbose_name="Curso")
    balance_from_previous_term = models.IntegerField(default=0, verbose_name="Saldo del periodo anterior")
    status = models.CharField(
        max_length=20,
        choices=[("activo", "Activo"), ("cerrado", "Cerrado")],
        default="activo",
        verbose_name="Estado",
    )

    class Meta:
        ordering = ["student", "term"]

    def __str__(self):
        return f"{self.student}"

    def balance(self):
        payable = self.total_amount_payable()
        paid = self.total_amount_paid()
        return payable - paid

    def amount_payable(self):
        items = InvoiceItem.objects.filter(invoice=self)
        total = 0
        for item in items:
            total += item.amount
        return total

    def total_amount_payable(self):
        return self.balance_from_previous_term + self.amount_payable()

    def total_amount_paid(self):
        receipts = Receipt.objects.filter(invoice=self)
        amount = 0
        for receipt in receipts:
            amount += receipt.amount_paid
        return amount

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"pk": self.pk})


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Factura")
    description = models.CharField(max_length=200, verbose_name="Descripción")
    amount = models.IntegerField(verbose_name="Monto")


class Receipt(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Factura")
    amount_paid = models.IntegerField(verbose_name="Monto Pagado")
    date_paid = models.DateField(default=timezone.now, verbose_name="Fecha de Pago")
    comment = models.CharField(max_length=200, blank=True, verbose_name="Comentario")

    def __str__(self):
        return f"Recibo en {self.date_paid}"
