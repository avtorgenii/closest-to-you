import json

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from shop.models import Product


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

    discount = 10
    total_price_after_discount = total_price * (1 - discount / 100)

    return render(request, 'shop/clients/finalize_purchase.html', {
        'basket_items': basket,
        'total_price': total_price_after_discount,
        'discount': discount,
    })