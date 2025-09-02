from django.shortcuts import render, redirect
from .models import Invoice, Customer, ServiceItem
from .forms import InvoiceForm, ServiceItemFormSet

from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.conf import settings
import os
import shutil
from pathlib import Path


from django.templatetags.static import static
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required



# Helper to resolve static paths for xhtml2pdf
def link_callback(uri, rel):
    path = finders.find(uri.replace(settings.STATIC_URL, ""))
    if path:
        return path
    return uri  # fallback



def generate_invoice_pdf(context, filename):
    template_path = 'invoices/pdf_template.html'  # adjust if needed
    html = render_to_string(template_path, context)

    output_path = os.path.join(settings.MEDIA_ROOT, 'invoices', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        result = pisa.CreatePDF(html, dest=f, link_callback=link_callback  
)

    return output_path if not result.err else None

@login_required
def create_invoice(request):
    if request.method == "POST":
        invoice_form = InvoiceForm(request.POST)
        formset = ServiceItemFormSet(request.POST)

        if invoice_form.is_valid() and formset.is_valid():
            # Create or get customer
            customer, created = Customer.objects.get_or_create(
                email=invoice_form.cleaned_data['customer_email'],
                defaults={
                    "name": invoice_form.cleaned_data['customer_name'],
                    "phone": invoice_form.cleaned_data['customer_phone'],
                    "address": invoice_form.cleaned_data['customer_address']
                }
            )

            # Save invoice without committing total yet
            invoice = invoice_form.save(commit=False)
            invoice.customer = customer
            invoice.total = 0  # fallback
            invoice.save()

            total_cost = 0
            services = formset.save(commit=False)

            for service in services:
                service.invoice = invoice
                service.save()  # ❗️ Moved inside the loop
                total_cost += service.cost or 0

            invoice.total = total_cost
            invoice.save()

            # Prepare data for template
            items = invoice.items.all()
            keywords = any(item.keywords for item in items)
            datalinks = any(item.datalinks for item in items)
            targeted_search_engine = any(item.targeted_search_engine for item in items)

            context = {
                "customer": {
                    "name": invoice.customer.name,
                    "address": invoice.customer.address,
                    "phone": invoice.customer.phone,
                    "email": invoice.customer.email
                },
                "invoice_no": invoice.invoice_no,
                "date": invoice.date.strftime("%d/%m/%Y"),
                "items": items,
                "total": invoice.total,
                "duration": invoice.duration,
                "payment_link": invoice.payment_link,
                "keywords": keywords,
                "datalinks": datalinks,
                "targeted_search_engine": targeted_search_engine,
                "STATIC_ROOT": os.path.join(settings.BASE_DIR, 'static')
            }

            # Generate PDF
            pdf_filename = f"invoice_{invoice.invoice_no}.pdf"
            pdf_path = generate_invoice_pdf(context, pdf_filename)

            if pdf_path and os.path.exists(pdf_path):
                invoice.pdf_file = f"invoices/{pdf_filename}"
                invoice.save()

            return redirect("invoice-list")

        else:
            # Debug: Print errors
            print("Invoice form errors:", invoice_form.errors)
            print("Formset errors:", formset.errors)

    else:
        invoice_form = InvoiceForm()
        formset = ServiceItemFormSet()

    return render(request, "invoices/create_invoice.html", {
        "invoice_form": invoice_form,
        "formset": formset
    })

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date')
    return render(request, "invoices/invoice_list.html", {"invoices": invoices})
