# tests/test_services.py
import pytest
from decimal import Decimal
from django.test import TestCase
from shop.models import *
from ..services.basket_service import BasketService
from ..services.purchase_service import PurchaseService
from ..services.order_service import OrderService
from ..services.checkout_service import CheckoutService



class BasketServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        vat = VAT.objects.create(value=5)
        category = ProductCategory.objects.create(name='Food')
        discount = Decimal('0')
        Product.objects.bulk_create([
            Product(id=3, name='Sałata', price=Decimal('4'), category=category, vat=vat, discount=discount),
            Product(id=4, name='Ser', price=Decimal('5'), category=category, vat=vat, discount=discount),
            Product(id=5, name='Masło', price=Decimal('9'), category=category, vat=vat, discount=discount),
        ])

    def test_get_hardcoded_basket(self):
        items, total = BasketService.get_hardcoded_basket()

        assert len(items) == 3
        assert items[0]['name'] == 'Sałata'
        assert total == Decimal(37)


class PurchaseServiceTest(TestCase):
    def test_calculate_final_prices(self):
        result = PurchaseService.calculate_final_prices(100.0)

        assert result['delivery_price'] == 7.0
        assert result['discount'] == 10.0
        assert result['total_after_discount'] == pytest.approx((100 + 7) * 0.9)




class CheckoutServiceTest(TestCase):
    def test_validate_and_extract_data_valid(self):
        class MockRequest:
            COOKIES = {
                'city': 'Kraków',
                'street': 'Rynek',
                'house_number': '1',
                'postal_code': '31-042',
                'planned_delivery_time': '2024-03-01 12:00',
                'delivery_leave_place': '1',
                'total_price': '100.0',
                'delivery_price': '7.0',
                'payment_method': 'card',
                'basket_items': '[{"id": 1, "quantity": 2}]'
            }

        data = CheckoutService.validate_and_extract_data(MockRequest())

        assert data['address']['city'] == 'Kraków'
        assert data['basket'] == [{'id': 1, 'quantity': 2}]

    def test_validate_and_extract_data_invalid(self):
        class MockRequest:
            COOKIES = {'total_price': 'invalid'}

        with pytest.raises(ValueError):
            CheckoutService.validate_and_extract_data(MockRequest())