import json

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal
from shop.models import *


def client_basket(request):

    basket_items = []
    total_price = 0

    product_lettuce = Product.objects.get(id=3)
    basket_items.append({
        'id': 3,
        'name': product_lettuce.name,
        'price': float(product_lettuce.price),
        'quantity': 1,
        'total': float(product_lettuce.price) * 1,
    })

    product_cheese = Product.objects.get(id=4)
    basket_items.append({
        'id': 4,
        'name': product_cheese.name,
        'price': float(product_cheese.price),
        'quantity': 3,
        'total': float(product_cheese.price) * 3,
    })

    product_butter = Product.objects.get(id=5)
    basket_items.append({
        'id': 5,
        'name': product_butter.name,
        'price': float(product_butter.price),
        'quantity': 2,
        'total': float(product_butter.price) * 2,
    })

    for item in basket_items:
        total_price += item['total']


    response = render(request, 'shop/clients/basket.html', {
        'basket_items': basket_items,
        'total_price': total_price,
    })
    response.set_cookie('basket_items', json.dumps(basket_items))
    response.set_cookie('total_price', total_price)
    return response

def client_finalize_purchase(request):
    basket = json.loads(request.COOKIES.get('basket_items', '[]'))
    total_price = float(request.COOKIES.get('total_price', 0))
    delivery_leave_places = DeliveryLeavePlace.objects.all()

    delivery_price = 7
    discount = 10
    total_price_after_discount = (total_price + delivery_price) * (1 - discount / 100)

    response = render(request, 'shop/clients/finalize_purchase.html', {
        'basket_items': basket,
        'total_price': total_price_after_discount,
        'delivery_price': delivery_price,
        'discount': discount,
        'delivery_leave_places': delivery_leave_places
    })

    response.set_cookie('total_price', str(total_price_after_discount))
    response.set_cookie('delivery_price', str(delivery_price))
    response.set_cookie('discount', str(discount))
    response.set_cookie('basket_items', json.dumps(basket))
    response.set_cookie('delivery_leave_places', json.dumps([{ 'id': place.id, 'name': place.name } for place in delivery_leave_places], default=str))
    return response

def client_checkout(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        street = request.POST.get('street')
        house_number = request.POST.get('house_number')
        apartment_number = request.POST.get('apartment_number')
        delivery_type = request.POST.get('delivery_type')
        planned_delivery_time = request.POST.get('planned_delivery_time')
        payment_method = request.POST.get('payment_method')
        invoice = request.POST.get('invoice')
        delivery_leave_place = request.POST.get('delivery_type')
        basket_items = json.loads(request.COOKIES.get('basket_items', '[]'))
        delivery_price = float(request.COOKIES.get('delivery_price', 0))
        total_price = float(request.COOKIES.get('total_price', 0))
        discount = float(request.COOKIES.get('discount', 0))

        if payment_method == 'card' and not invoice:
            response = render(request, 'shop/clients/checkout_creditcard.html')
            response.set_cookie('first_name', first_name)
            response.set_cookie('last_name', last_name)
            response.set_cookie('postal_code', postal_code)
            response.set_cookie('city', city)
            response.set_cookie('street', street)
            response.set_cookie('house_number', house_number)
            response.set_cookie('apartment_number', apartment_number)
            response.set_cookie('delivery_type', delivery_type)
            response.set_cookie('planned_delivery_time', planned_delivery_time)
            response.set_cookie('payment_method', payment_method)
            response.set_cookie('invoice', invoice)
            response.set_cookie('basket_items', json.dumps(basket_items))
            response.set_cookie('delivery_price', str(delivery_price))
            response.set_cookie('total_price', str(total_price))
            response.set_cookie('discount', str(discount))
            response.set_cookie('delivery_leave_place', delivery_leave_place)
            return response

        elif payment_method == 'card' and invoice:
            response = render(request, 'shop/clients/checkout_creditcard.html')
            response.set_cookie('first_name', first_name)
            response.set_cookie('last_name', last_name)
            response.set_cookie('postal_code', postal_code)
            response.set_cookie('city', city)
            response.set_cookie('street', street)
            response.set_cookie('house_number', house_number)
            response.set_cookie('apartment_number', apartment_number)
            response.set_cookie('delivery_type', delivery_type)
            response.set_cookie('planned_delivery_time', planned_delivery_time)
            response.set_cookie('payment_method', payment_method)
            response.set_cookie('invoice', invoice)
            response.set_cookie('basket_items', json.dumps(basket_items))
            response.set_cookie('delivery_price', str(delivery_price))
            response.set_cookie('total_price', str(total_price))
            response.set_cookie('discount', str(discount))
            response.set_cookie('delivery_leave_place', delivery_leave_place)
            response.set_cookie('country', request.GET.get('country'))
            response.set_cookie('nip', request.GET.get('nip'))
            response.set_cookie('company', request.GET.get('company'))
            response.set_cookie('company_zip_code', request.GET.get('zip_code'))
            response.set_cookie('address', request.GET.get('address'))
            return response


        elif payment_method == 'operator' and invoice:
            response = render(request, 'shop/clients/checkout_transfer.html')
            response.set_cookie('first_name', first_name)
            response.set_cookie('last_name', last_name)
            response.set_cookie('postal_code', postal_code)
            response.set_cookie('city', city)
            response.set_cookie('street', street)
            response.set_cookie('house_number', house_number)
            response.set_cookie('apartment_number', apartment_number)
            response.set_cookie('delivery_type', delivery_type)
            response.set_cookie('planned_delivery_time', planned_delivery_time)
            response.set_cookie('payment_method', payment_method)
            response.set_cookie('invoice', invoice)
            response.set_cookie('basket_items', json.dumps(basket_items))
            response.set_cookie('delivery_price', str(delivery_price))
            response.set_cookie('total_price', str(total_price))
            response.set_cookie('discount', str(discount))
            response.set_cookie('delivery_leave_place', delivery_leave_place)
            response.set_cookie('country', request.GET.get('country'))
            response.set_cookie('nip', request.GET.get('nip'))
            response.set_cookie('company', request.GET.get('company'))
            response.set_cookie('company_zip_code', request.GET.get('zip_code'))
            response.set_cookie('address', request.GET.get('address'))
            return response

        else:
            response = render(request, 'shop/clients/checkout_transfer.html')
            response.set_cookie('first_name', first_name)
            response.set_cookie('last_name', last_name)
            response.set_cookie('postal_code', postal_code)
            response.set_cookie('city', city)
            response.set_cookie('street', street)
            response.set_cookie('house_number', house_number)
            response.set_cookie('apartment_number', apartment_number)
            response.set_cookie('delivery_type', delivery_type)
            response.set_cookie('planned_delivery_time', planned_delivery_time)
            response.set_cookie('payment_method', payment_method)
            response.set_cookie('invoice', invoice)
            response.set_cookie('basket_items', json.dumps(basket_items))
            response.set_cookie('delivery_price', str(delivery_price))
            response.set_cookie('total_price', str(total_price))
            response.set_cookie('discount', str(discount))
            response.set_cookie('delivery_leave_place', delivery_leave_place)
            return response

def process_payment(request):
    if request.method == 'POST':
        first_name = request.COOKIES.get('first_name')
        last_name = request.COOKIES.get('last_name')
        postal_code = request.COOKIES.get('postal_code')
        city = request.COOKIES.get('city')
        street = request.COOKIES.get('street')
        house_number = request.COOKIES.get('house_number')
        apartment_number = request.COOKIES.get('apartment_number')
        try:
            apartment_number = int(apartment_number) if apartment_number else None
        except ValueError:
            apartment_number = None
        delivery_type = request.COOKIES.get('delivery_type')
        planned_delivery_time = request.COOKIES.get('planned_delivery_time')
        payment_method = request.COOKIES.get('payment_method')
        invoice = request.COOKIES.get('invoice')
        basket_items = json.loads(request.COOKIES.get('basket_items', '[]'))
        delivery_price = float(request.COOKIES.get('delivery_price', 0))
        total_price = float(request.COOKIES.get('total_price', 0))
        discount = float(request.COOKIES.get('discount', 0))
        delivery_leave_place = request.COOKIES.get('delivery_leave_place')

        current_user = Client.objects.get(id=1)

        order = Order.objects.create(
            client=current_user,
            total_price=total_price,
            delivery_price=delivery_price
        )
        loyalty_points_to_add = int(total_price)
        client = Client.objects.get(id=1)
        Client.objects.update(id=1, loyalty_points=client.loyalty_points + loyalty_points_to_add)
        client.save()

        for item in basket_items:
            product = Product.objects.get(id=item['id'])
            OrderProduct.objects.create(order=order, product=product, quantity=item['quantity'])

        # Tworzenie dostawy
        address = Address.objects.create(
            city=city,
            street=street,
            house_number=house_number,
            apartment_number=apartment_number,
            postal_code=postal_code
        )
        delivery_leave_place = DeliveryLeavePlace.objects.get(id=delivery_leave_place)
        delivery_stage = DeliveryStage.objects.get(id=4)


        Delivery.objects.create(
            planned_time=planned_delivery_time,
            order=order,
            address=address,
            delivery_leave_place=delivery_leave_place,
            delivery_stage=delivery_stage
        )

        Payment.objects.create(
            order=order,
            payment_type=PaymentType.objects.get(name=payment_method)
        )
        return render(request, 'shop/clients/order_success.html', {
            'loyalty_points': int(total_price),
            'order_id': order.id
        })


    return render(request, 'shop/clients/order_failed.html')