from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import json

from shop.models import *
from ..services.basket_service import BasketService
from ..services.checkout_service import CheckoutService
from ..services.purchase_service import PurchaseService
from ..services.order_service import OrderService


def client_basket(request):
    basket_items, total_price = BasketService.get_hardcoded_basket()

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

    purchase_details = PurchaseService.calculate_final_prices(total_price)
    delivery_leave_places = DeliveryLeavePlace.objects.all()

    response = render(request, 'shop/clients/finalize_purchase.html', {
        **purchase_details,
        'basket_items': basket,
        'delivery_leave_places': delivery_leave_places
    })

    # Ustawianie ciasteczek
    for key, value in purchase_details.items():
        response.set_cookie(key, str(value))
    return response


def process_payment(request):
    if request.method == 'POST':
        try:
            # Walidacja i ekstrakcja danych
            order_data = CheckoutService.validate_and_extract_data(request)

            # Pobierz klienta (tymczasowe rozwiązanie - powinno być z sesji)
            client = Client.objects.get(id=1)

            # Utwórz zamówienie
            order = OrderService.create_order(
                client=client,
                **order_data
            )

            return render(request, 'shop/clients/order_success.html', {
                'loyalty_points': int(order_data['payment']['total_price']),
                'order_id': order.id
            })

        except Client.DoesNotExist:
            print("Klient nie istnieje")
            return render(request, 'shop/clients/order_failed.html')

        except DeliveryLeavePlace.DoesNotExist:
            print("Nieprawidłowy punkt odbioru")
            return render(request, 'shop/clients/order_failed.html')

        except ValueError as e:
            print(f"Błąd danych: {str(e)}")
            return render(request, 'shop/clients/order_failed.html')

        except Exception as e:
            print(f"Krytyczny błąd systemu: {str(e)}")
            return render(request, 'shop/clients/order_failed.html')

    return render(request, 'shop/clients/order_failed.html')

def client_checkout(request):
    if request.method != 'POST':
        return render(request, 'shop/clients/checkout_transfer.html')

    # Pobieranie danych z formularza
    post_data = {key: value for key, value in request.POST.items()}
    cookies_to_set = {
        'first_name': post_data.get('first_name'),
        'last_name': post_data.get('last_name'),
        'postal_code': post_data.get('postal_code'),
        'city': post_data.get('city'),
        'street': post_data.get('street'),
        'house_number': post_data.get('house_number'),
        'apartment_number': post_data.get('apartment_number'),
        'delivery_type': post_data.get('delivery_type'),
        'planned_delivery_time': post_data.get('planned_delivery_time'),
        'payment_method': post_data.get('payment_method'),
        'invoice': post_data.get('invoice'),
        'delivery_leave_place': post_data.get('delivery_leave_place'),
    }

    # Określanie szablonu odpowiedzi
    template = 'shop/clients/checkout_transfer.html'
    if post_data.get('payment_method') == 'card':
        template = 'shop/clients/checkout_creditcard.html'

    # Dodatkowe dane dla faktury
    if post_data.get('invoice'):
        invoice_fields = {
            'country': post_data.get('country'),
            'nip': post_data.get('nip'),
            'company': post_data.get('company'),
            'company_zip_code': post_data.get('zip_code'),
            'address': post_data.get('address'),
        }
        cookies_to_set.update(invoice_fields)

    # Przygotowanie odpowiedzi
    response = render(request, template)

    # Ustawianie ciasteczek
    for key, value in cookies_to_set.items():
        if value:
            response.set_cookie(key, value)

    # Dodatkowe ciasteczka z koszykiem
    basket_cookies = {
        'basket_items': request.COOKIES.get('basket_items'),
        'delivery_price': request.COOKIES.get('delivery_price'),
        'total_price': request.COOKIES.get('total_price'),
        'discount': request.COOKIES.get('discount'),
    }
    for key, value in basket_cookies.items():
        if value:
            response.set_cookie(key, value)

    return response