from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=100, unique=True)
    date = models.DateField(default=timezone.now, editable=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True)
    payment_option = models.CharField(max_length=50)
    payment_link = models.URLField(blank=True)
    pdf_file = models.FileField(upload_to="invoices/", blank=True, null=True)


    def __str__(self):
        return f"Invoice {self.invoice_no} for {self.customer.name}"

class ServiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    service = models.CharField(max_length=255)
    project = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    keywords = models.PositiveIntegerField(blank=True, null=True)
    datalinks = models.PositiveIntegerField(blank=True, null=True)
    targeted_search_engine = models.PositiveIntegerField(blank=True, null=True)
