from django import forms
from apps.finance.models import Invoice, InvoiceItem, Receipt

class PaymentHistoryForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = []
