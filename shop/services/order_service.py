from django.db import transaction

from shop.models import *


class OrderService:
    @staticmethod
    def create_order(client, address, delivery, payment, basket):
        with transaction.atomic():
            # Aktualizacja punktów lojalnościowych
            client.loyalty_points += int(payment['total_price'])
            client.save()

            # Utwórz zamówienie
            order = Order.objects.create(
                client=client,
                total_price=payment['total_price'],
                delivery_price=payment['delivery_price']
            )

            # Produkty w zamówieniu
            for item in basket:
                product = Product.objects.get(id=item['id'])
                OrderProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity']
                )

            # Adres
            address_obj = Address.objects.create(**address)

            # Dostawa
            Delivery.objects.create(
                planned_time=delivery['planned_delivery_time'],
                order=order,
                address=address_obj,
                delivery_leave_place_id=delivery['delivery_leave_place'],
                delivery_stage_id=1
            )

            # Płatność
            Payment.objects.create(
                order=order,
                payment_type=PaymentType.objects.get(name=payment['payment_method'])
            )

            return order