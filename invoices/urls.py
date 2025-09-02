from django.urls import path
from . import views

urlpatterns = [
    path("create-invoice/", views.create_invoice, name="invoice-create"),
    path("list/", views.invoice_list, name="invoice-list"),
]
