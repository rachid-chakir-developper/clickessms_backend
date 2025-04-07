# Exemple dans views.py
from django.shortcuts import render

def invoice_pdf(request):
    return render(request, 'sales/invoice.html')  # le template HTML dans /templates/
