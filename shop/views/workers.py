from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from shop.models import Complaint, Delivery, Product, Incident, Order, OrderProduct, Worker

basket = [
    {'product': 'Milk', 'quantity': 1},
    {'product': 'Twix', 'quantity': 2},
]

@login_required()
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
    chat_messages = [
        {'sender': 'Courier', 'message': 'Wypadek podczas dostawy, złamałem nogę, proszę o dalsze instrukcję'},
    ]

    delivery = Delivery.objects.get(pk=d_id)
    order = delivery.order
    order_products = order.order_products.all()
    courier = delivery.deliverer
    client = order.client
    incident = delivery.incidents.last()

    context = {
        'd_id': d_id,
        'delivery': delivery,
        "order": order,
        "order_products": order_products,
        'courier': courier,
        'client': client,
        'chat_messages': chat_messages,
        'incident': incident,
        'basket': basket
    }

    return render(request, 'shop/workers/delivery.html', context)


def confirm_incident(request, d_id):
    delivery = Delivery.objects.get(pk=d_id)
    deliverer_id = delivery.deliverer.pk
    support_worker_id = request.user.worker_profile.pk

    Incident.objects.create(description="Incident", delivery_id=d_id, deliverer_id=deliverer_id,
                            support_worker_id=support_worker_id)

    return HttpResponse("Ok", status=200)


@csrf_exempt
def courier_compensation(request, c_id):
    print("courier_compensation")
    return HttpResponse("Ok", status=200)


@csrf_exempt
def client_compensation(request, c_id):
    print("client_compensation")
    return HttpResponse("Ok", status=200)


def confirm_order_and_delivery(request, o_id, d_id):
    if request.method == "POST":
        # Extract data from the form
        planned_time = request.POST.get('plannedTime')
        same_deliverer = request.POST.get('deliverer') == 'on'  # Checkbox returns 'on' if checked
        deliverer_id = int(request.POST.get('delivererId'))
        client_id = int(request.POST.get('clientId'))

        try:
            # Parse planned_time to a Python datetime object
            planned_time = datetime.fromisoformat(planned_time) if planned_time else None

            if planned_time:
                deliverer_id = deliverer_id if same_deliverer else None

                # Previous order
                old_order = Order.objects.get(pk=o_id)

                # Order instance
                order = Order.objects.create(total_price=15, delivery_price=1, client_id=client_id)

                for product_quantity in basket:
                    product = Product.objects.get(name=product_quantity['product'])
                    OrderProduct.objects.create(product=product, quantity=product_quantity['quantity'], order=order)

                # Previous delivery
                old_delivery = Delivery.objects.get(pk=d_id)

                # Delivery instance
                delivery = Delivery.objects.create(
                    planned_time=planned_time,
                    deliverer_id=deliverer_id,
                    client_id=client_id,
                    address=old_delivery.address,
                    delivery_leave_place=old_delivery.delivery_leave_place,
                    order=order
                )

            return HttpResponse("Order and delivery confirmed!", status=200)
        except ValueError as e:
            # Handle invalid datetime format or other issues
            return HttpResponse(f"Invalid data: {e}", status=400)

    return HttpResponse("Invalid request method", status=405)
