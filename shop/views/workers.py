from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from shop.models import Complaint
from shop.services import *


def is_support_worker(user):
    if not user.is_authenticated:
       return False # redirects to login
    if not hasattr(user, 'worker_profile'):
        raise PermissionDenied("You are not a registered worker.") # raises 403
    if user.worker_profile.role.name != 'Support':
        raise PermissionDenied("You do not have the 'Support' role.") # raises 403
    return True # allows


@user_passes_test(is_support_worker)
def support_dashboard(request):
    context = {
        'complaints': Complaint.objects.all().order_by('-pk'),
        'deliveries': Delivery.objects.all().order_by('-pk'),
    }
    return render(request, 'shop/workers/support_dashboard.html', context)


@user_passes_test(is_support_worker)
def complaint(request, c_id):
    complaint = get_object_or_404(Complaint, pk=c_id)
    order = complaint.order if hasattr(complaint, 'order') else None
    order_products = order.order_products.all() if order else None
    delivery = order.delivery if order else None

    context = {
        'c_id': c_id,
        'client': complaint.client,
        'complaint': complaint,
        'order': order,
        'order_products': order_products,
        'delivery': delivery
    }
    return render(request, 'shop/workers/complaint.html', context)


@user_passes_test(is_support_worker)
def decline_complaint(request, c_id):
    complaint = get_object_or_404(Complaint, pk=c_id)
    decline_complaint_service(
        complaint=complaint,
        worker=request.user.worker_profile,
        resolution_text=request.POST.get('response', '')
    )
    return redirect('support_dashboard')


@user_passes_test(is_support_worker)
def accept_complaint(request, c_id):
    complaint = get_object_or_404(Complaint, pk=c_id)
    accept_complaint_service(
        complaint=complaint,
        worker=request.user.worker_profile,
        compensation_str=request.POST.get('compensation', '0'),
        is_refund='refund' in request.POST
    )
    return redirect('support_dashboard')


@user_passes_test(is_support_worker)
def delivery(request, d_id):
    delivery = get_object_or_404(Delivery, pk=d_id)
    order = delivery.order
    incident = delivery.incidents.last()
    chat_messages = [{'sender': 'Courier', 'message': '...'}]  # Example data

    context = {
        'd_id': d_id,
        'delivery': delivery,
        "order": order,
        "order_products": order.order_products.all(),
        'courier': delivery.deliverer,
        'client': order.client,
        'chat_messages': chat_messages,
        'incident': incident,
        'products': Product.objects.all()
    }
    return render(request, 'shop/workers/delivery.html', context)


@user_passes_test(is_support_worker)
def confirm_incident(request, d_id):
    delivery = get_object_or_404(Delivery, pk=d_id)
    create_incident(delivery=delivery, support_worker=request.user.worker_profile)
    return HttpResponse("Ok", status=200)


@user_passes_test(is_support_worker)
@csrf_exempt
def courier_compensation(request, c_id):
    compensation_str = request.POST.get('compensation', '0')
    success, error = add_courier_compensation(c_id, compensation_str)
    if not success:
        return JsonResponse({'error': error}, status=400)
    return HttpResponse("Ok", status=200)


@user_passes_test(is_support_worker)
@csrf_exempt
def client_compensation(request, c_id):
    compensation_str = request.POST.get('compensation', '0')
    success, error = add_client_compensation(c_id, compensation_str)
    if not success:
        return JsonResponse({'error': error}, status=400)
    return HttpResponse("Ok", status=200)


@user_passes_test(is_support_worker)
@csrf_exempt
def confirm_order_and_delivery(request, d_id):
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=405)

    products_data = {
        int(key.split('_')[1]): int(value)
        for key, value in request.POST.items()
        if key.startswith('product_')
    }

    try:
        recreate_order_and_delivery(
            old_delivery_id=d_id,
            planned_time_str=request.POST.get('plannedTime'),
            same_deliverer=request.POST.get('deliverer') == 'on',
            deliverer_id=int(request.POST.get('delivererId', 0)),
            client_id=int(request.POST.get('clientId')),
            products_data=products_data
        )
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=400)

    return HttpResponse("Order and delivery confirmed!", status=200)
