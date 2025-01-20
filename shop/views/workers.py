from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, redirect

from shop.models import Complaint, Delivery


def support_dashboard(request):
    context = {
        'complaints': Complaint.objects.all().order_by('-pk'),
        'deliveries': Delivery.objects.all().order_by('-pk'),
    }
    return render(request, 'shop/workers/support_dashboard.html', context)


def complaint(request, c_id):
    complaint = Complaint.objects.get(pk=c_id)
    order = complaint.order if hasattr(complaint, 'order') else None
    order_products = order.order_products.all() if order else None
    deliveries = order.deliveries.all() if order else None

    for delivery in deliveries:
        print(delivery)

    context = {
        'c_id': c_id,
        'client': complaint.client,
        'complaint': complaint,
        'order': order,
        'order_products': order_products,
        'deliveries': deliveries
    }
    return render(request, 'shop/workers/complaint.html', context)

def decline_complaint(request, c_id):
    complaint = Complaint.objects.get(pk=c_id)

    complaint.resolution_date = datetime.now()
    complaint.resolution = request.POST.get('response', '')
    complaint.worker_id = request.user.worker_profile.pk
    complaint.save()

    return redirect('support_dashboard')

def accept_complaint(request, c_id):
    complaint = Complaint.objects.get(pk=c_id)

    complaint.resolution_date = datetime.now()
    complaint.resolution = 'Accepted'
    complaint.worker_id = request.user.worker_profile.pk

    compensation = request.POST.get('compensation', '0')
    try:
        compensation = Decimal(compensation)
    except:
        compensation = Decimal(0)

    is_refund = 'refund' in request.POST
    refund = Decimal(complaint.order.total_price) if is_refund else Decimal(0)

    complaint.client.loyalty_points += (compensation + refund)

    complaint.client.save()
    complaint.save()

    return redirect('support_dashboard')



def delivery(request, d_id):
    return None