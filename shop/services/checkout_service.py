import json


class CheckoutService:
    @staticmethod
    def validate_and_extract_data(request):
        try:
            # Ekstrakcja danych adresowych
            address_data = {
                'city': request.COOKIES.get('city'),
                'street': request.COOKIES.get('street'),
                'house_number': request.COOKIES.get('house_number'),
                'apartment_number': request.COOKIES.get('apartment_number') or None,
                'postal_code': request.COOKIES.get('postal_code')
            }

            # Ekstrakcja danych dostawy
            delivery_data = {
                'planned_delivery_time': request.COOKIES.get('planned_delivery_time'),
                'delivery_leave_place': int(request.COOKIES.get('delivery_leave_place'))
            }

            # Ekstrakcja danych płatności
            payment_data = {
                'total_price': float(request.COOKIES.get('total_price', 0)),
                'delivery_price': float(request.COOKIES.get('delivery_price', 0)),
                'payment_method': request.COOKIES.get('payment_method')
            }

            # Ekstrakcja koszyka
            basket_data = json.loads(request.COOKIES.get('basket_items', '[]'))

            return {
                'address': address_data,
                'delivery': delivery_data,
                'payment': payment_data,
                'basket': basket_data
            }

        except (TypeError, ValueError, KeyError) as e:
            raise ValueError(f"Błędne dane: {str(e)}")

    @staticmethod
    def handle_invoice_data(request):
        if not request.POST.get('invoice'):
            return {}

        return {
            'country': request.POST.get('country'),
            'nip': request.POST.get('nip'),
            'company': request.POST.get('company'),
            'company_zip_code': request.POST.get('zip_code'),
            'address': request.POST.get('address')
        }