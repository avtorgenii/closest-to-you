from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from shop.models import Complaint, Delivery, Product, Incident, Order, OrderProduct, Worker, Client


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

    complaint.client.compensations += (compensation + refund)

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
    products = Product.objects.all()

    context = {
        'd_id': d_id,
        'delivery': delivery,
        "order": order,
        "order_products": order_products,
        'courier': courier,
        'client': client,
        'chat_messages': chat_messages,
        'incident': incident,
        'products': products
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
    compensation = request.POST.get('compensation')
    try:
        compensation = Decimal(compensation)
        if compensation < 0:
            return JsonResponse({'error': 'Compensation cannot be negative.'}, status=400)
    except (InvalidOperation, TypeError):
        return JsonResponse({'error': 'Invalid compensation value.'}, status=400)

    courier = Worker.objects.get(pk=c_id)
    incident = courier.deliverer_incidents.last()
    incident.deliverer_compensation += compensation
    incident.save()

    return HttpResponse("Ok", status=200)


@csrf_exempt
def client_compensation(request, c_id):
    compensation = request.POST.get('compensation')
    try:
        compensation = Decimal(compensation)
        if compensation < 0:
            return JsonResponse({'error': 'Compensation cannot be negative.'}, status=400)
    except (InvalidOperation, TypeError):
        return JsonResponse({'error': 'Invalid compensation value.'}, status=400)

    client = Client.objects.get(pk=c_id)
    client.compensations += compensation
    client.save()

    return HttpResponse("Ok", status=200)


def confirm_order_and_delivery(request, d_id):
    if request.method == "POST":
        # Extract data from the form
        planned_time = request.POST.get('plannedTime')
        same_deliverer = request.POST.get('deliverer') == 'on'
        deliverer_id = int(request.POST.get('delivererId'))
        client_id = int(request.POST.get('clientId'))

        try:
            planned_time = datetime.fromisoformat(planned_time) if planned_time else None

            # Fetch the client and deliverer objects
            client = get_object_or_404(Client, pk=client_id)
            deliverer = get_object_or_404(Worker, pk=deliverer_id) if not same_deliverer else get_object_or_404(Worker,
                                                                                                                pk=deliverer_id)

            # Create a new Order instance
            order = Order.objects.create(delivery_price=1, client=client)  # hard-coded delivery price

            # Extract the product quantities from the POST data
            for product_id, quantity in request.POST.items():
                if product_id.startswith('product_'):  # products are named as 'product_<product_id>'
                    product_id = int(product_id.split('_')[1])  # extract product ID
                    product = get_object_or_404(Product, pk=product_id)
                    quantity = int(quantity)

                    # Create an OrderProduct instance linking the order, product, and quantity
                    OrderProduct.objects.create(product=product, quantity=quantity, order=order)

            order.update_total_price()  # calculate the total price in the model

            old_delivery = get_object_or_404(Delivery, pk=d_id)

            Delivery.objects.create(
                planned_time=planned_time,
                deliverer=deliverer,
                address=old_delivery.address,
                delivery_leave_place=old_delivery.delivery_leave_place,
                order=order
            )

            return HttpResponse("Order and delivery confirmed!", status=200)

        except ValueError as e:
            # Handle invalid datetime format or other issues
            return HttpResponse(f"Invalid data: {e}", status=400)

    return HttpResponse("Invalid request method", status=405)
