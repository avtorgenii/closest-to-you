from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from shop.models import Incident, Order, OrderProduct, Delivery, Worker, Client, Product


def decline_complaint_service(complaint, worker, resolution_text):
    complaint.resolution_date = timezone.now()
    complaint.resolution = resolution_text
    complaint.worker = worker
    complaint.save()


def accept_complaint_service(complaint, worker, compensation_str, is_refund):
    try:
        compensation = Decimal(compensation_str)
    except InvalidOperation:
        compensation = Decimal(0)

    complaint.resolution_date = timezone.now()
    complaint.resolution = 'Accepted'
    complaint.worker = worker

    refund = complaint.order.total_price if is_refund else Decimal(0)
    total_compensation = compensation + refund

    client = complaint.client
    client.compensations += total_compensation
    client.save()

    complaint.save()


def create_incident(delivery, support_worker):
    Incident.objects.create(
        description="Incident",
        delivery=delivery,
        deliverer=delivery.deliverer,
        support_worker=support_worker
    )


def add_courier_compensation(courier_id, compensation_str):
    try:
        compensation = Decimal(compensation_str)
        if compensation < 0:
            return False, "Compensation cannot be negative."
    except InvalidOperation:
        return False, "Invalid compensation value."

    courier = Worker.objects.get(pk=courier_id)
    incident = courier.deliverer_incidents.last()
    if not incident:
        return False, "No incident found for courier."

    incident.deliverer_compensation += compensation
    incident.save()
    return True, None


def add_client_compensation(client_id, compensation_str):
    try:
        compensation = Decimal(compensation_str)
        if compensation < 0:
            return False, "Compensation cannot be negative."
    except InvalidOperation:
        return False, "Invalid compensation value."

    client = Client.objects.get(pk=client_id)
    client.compensations += compensation
    client.save()
    return True, None


@transaction.atomic
def recreate_order_and_delivery(old_delivery_id, planned_time_str, same_deliverer, deliverer_id, client_id,
                                products_data):
    old_delivery = Delivery.objects.get(pk=old_delivery_id)
    planned_time = datetime.fromisoformat(planned_time_str) if planned_time_str else None

    client = Client.objects.get(pk=client_id)
    order = Order.objects.create(delivery_price=Decimal('1'), client=client)

    for product_id, quantity in products_data.items():
        product = Product.objects.get(pk=product_id)
        OrderProduct.objects.create(product=product, quantity=quantity, order=order)

    order.update_total_price()

    if same_deliverer:
        deliverer = old_delivery.deliverer
    else:
        deliverer = Worker.objects.get(pk=deliverer_id)

    new_delivery = Delivery.objects.create(
        planned_time=planned_time,
        deliverer=deliverer,
        address=old_delivery.address,
        delivery_leave_place=old_delivery.delivery_leave_place,
        order=order
    )

    return new_delivery