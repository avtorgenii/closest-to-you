from django.shortcuts import render

def client_dashboard(request):
    return render(request, 'shop/clients/client_dashboard.html')