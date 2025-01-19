from django.shortcuts import render

from shop.models import Complaint, Delivery


def support_dashboard(request):
    context = {
        'complaints': Complaint.objects.all().order_by('-submission_date'),
        'deliveries': Delivery.objects.all().order_by('-delivery_time'),
    }
    return render(request, 'shop/workers/support_dashboard.html', context)


def complaint(request, c_id):
    return None

def delivery(request, d_id):
    return None