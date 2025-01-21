import json

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from shop.models import *


def client_basket(request):

    basket_items = []
    total_price = 0

    product_lettuce = Product.objects.get(id=3)
    basket_items.append({
        'id': 3,
        'name': product_lettuce.name,
        'price': product_lettuce.price,
        'quantity': 1,
        'total': product_lettuce.price * 1,
    })

    product_cheese = Product.objects.get(id=4)
    basket_items.append({
        'id': 4,
        'name': product_cheese.name,
        'price': product_cheese.price,
        'quantity': 3,
        'total': product_cheese.price * 3,
    })

    product_butter = Product.objects.get(id=5)
    basket_items.append({
        'id': 5,
        'name': product_butter.name,
        'price': product_butter.price,
        'quantity': 2,
        'total': product_butter.price * 2,
    })

    for item in basket_items:
        total_price += item['total']


    response = render(request, 'shop/clients/basket.html', {
        'basket_items': basket_items,
        'total_price': total_price,
    })
    response.set_cookie('basket_items', json.dumps(basket_items, default=str))
    response.set_cookie('total_price', total_price)
    return response

def client_finalize_purchase(request):
    basket = json.loads(request.COOKIES.get('basket_items', '[]'), parse_float=float)
    total_price = float(request.COOKIES.get('total_price', 0))
    delivery_leave_places = DeliveryLeavePlace.objects.all()

    delivery_price = 7
    discount = 10
    total_price_after_discount = (total_price + delivery_price) * (1 - discount / 100)

    return render(request, 'shop/clients/finalize_purchase.html', {
        'basket_items': basket,
        'total_price': total_price_after_discount,
        'delivery_price': delivery_price,
        'discount': discount,
        'delivery_leave_places': delivery_leave_places
    })

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
        basket_items = request.POST.get('basket_items')
        delivery_price = request.POST.get('delivery_price')
        total_price = request.POST.get('total_price')
        discount = request.POST.get('discount')
        delivery_leave_place = request.POST.get('delivery_leave_place')


        if payment_method == 'card' and not invoice:
            return render(request, 'shop/clients/checkout_creditcard.html', {
                'first_name': first_name,
                'last_name': last_name,
                'postal_code': postal_code,
                'city': city,
                'street': street,
                'house_number': house_number,
                'apartment_number': apartment_number,
                'delivery_type': delivery_type,
                'planned_delivery_time': planned_delivery_time,
                'basket_items': basket_items,
                'delivery_price': delivery_price,
                'total_price': total_price,
                'discount': discount,
                'delivery_leave_place': delivery_leave_place
            })

        elif payment_method == 'card' and invoice:
            return render(request, 'shop/clients/checkout_creditcard.html', {
                'first_name': first_name,
                'last_name': last_name,
                'postal_code': postal_code,
                'city': city,
                'street': street,
                'house_number': house_number,
                'apartment_number': apartment_number,
                'delivery_type': delivery_type,
                'planned_delivery_time': planned_delivery_time,
                'basket_items': basket_items,
                'delivery_price': delivery_price,
                'total_price': total_price,
                'discount': discount,
                'delivery_leave_place': delivery_leave_place,
                'country': request.GET.get('country'),
                'nip': request.GET.get('nip'),
                'company': request.GET.get('company'),
                'company_zip_code': request.GET.get('zip_code'),
                'address': request.GET.get('address')
            })

        elif payment_method == 'operator' and invoice:
            return render(request, 'shop/clients/checkout_transfer.html', {
                'first_name': first_name,
                'last_name': last_name,
                'postal_code': postal_code,
                'city': city,
                'street': street,
                'house_number': house_number,
                'apartment_number': apartment_number,
                'delivery_type': delivery_type,
                'planned_delivery_time': planned_delivery_time,
                'basket_items': basket_items,
                'delivery_price': delivery_price,
                'total_price': total_price,
                'discount': discount,
                'delivery_leave_place': delivery_leave_place,
                'country': request.GET.get('country'),
                'nip': request.GET.get('nip'),
                'company': request.GET.get('company'),
                'company_zip_code': request.GET.get('zip_code'),
                'address': request.GET.get('address')
            })

        else:
            return render(request, 'shop/clients/checkout_transfer.html', {
                'first_name': first_name,
                'last_name': last_name,
                'postal_code': postal_code,
                'city': city,
                'street': street,
                'house_number': house_number,
                'apartment_number': apartment_number,
                'delivery_type': delivery_type,
                'planned_delivery_time': planned_delivery_time,
                'basket_items': basket_items,
                'delivery_price': delivery_price,
                'total_price': total_price,
                'discount': discount,
                'delivery_leave_place': delivery_leave_place
            })

def process_payment(request):
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
        basket_items = request.POST.get('basket_items')
        delivery_price = request.POST.get('delivery_price')
        total_price = request.POST.get('total_price')
        discount = request.POST.get('discount')
        delivery_leave_place = request.POST.get('delivery_leave_place')
    return render(request, 'shop/clients/checkout.html')
        # if payment_method == 'card':
        #     card_number = request.POST.get('card_number')
        #     card_expiration_date = request.POST.get('card_expiration_date')
        #     card_cvv = request.POST.get('card_cvv')
        #
        #     return render(request, 'shop/clients/payment_success.html', {
        #         'first_name': first_name,
        #         'last_name': last_name,
        #         'postal_code': postal_code,
        #         'city': city,
        #         'street': street,
        #         'house_number': house_number,
        #         'apartment_number': apartment_number,
        #         'delivery_type': delivery_type,
        #         'planned_delivery_time': planned_delivery_time,
        #         'basket_items': basket_items,
        #         'delivery_price': delivery_price,
        #         'total_price': total_price,
        #         'discount': discount,
        #         'delivery_leave_place': delivery_leave_place,
        #         'card_number': card_number,
        #         'card_expiration_date': card_expiration_date,
        #         'card_cvv': card_cvv
        #     })
        #
        # elif payment_method == 'transfer':
        #     return render(request, 'shop/clients/payment_success.html', {
        #         'first_name': first_name,
        #         'last_name': last_name,
        #         'postal_code': postal_code,
        #         'city': city,
        #         'street': street,
        #         'house_number': house_number,
        #         'apartment_number': apartment_number,
        #         'delivery_type': delivery_type,
        #         'planned_delivery_time': planned_delivery_time,
        #         'basket_items': basket_items,
        #         'delivery_price': delivery_price,