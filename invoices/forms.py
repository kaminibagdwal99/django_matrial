from django import forms
from .models import Invoice, Customer, ServiceItem
from django.forms import inlineformset_factory

class InvoiceForm(forms.ModelForm):
    # Add Customer fields manually
    customer_name = forms.CharField(label="Customer Name", max_length=100)
    customer_email = forms.EmailField(label="Customer Email")
    customer_phone = forms.CharField(label="Customer Phone", max_length=15)
    customer_address = forms.CharField(label="Customer Address", widget=forms.Textarea)

    class Meta:
        model = Invoice
        fields = ['invoice_no', 'date', 'payment_option', 'duration', 'payment_link', 'total']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

# ✅ Custom form for service items
class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = ("service", "project", "cost", "keywords", "datalinks", "targeted_search_engine")
        widgets = {
            'keywords': forms.NumberInput(attrs={'placeholder': 'optional'}),
            'datalinks': forms.NumberInput(attrs={'placeholder': 'optional'}),
            'targeted_search_engine': forms.TextInput(attrs={'placeholder': 'optional'}),
        }

# ✅ Inline formset using custom form
ServiceItemFormSet = inlineformset_factory(
    Invoice,
    ServiceItem,
    form=ServiceItemForm,
    extra=1,
    can_delete=False
)
