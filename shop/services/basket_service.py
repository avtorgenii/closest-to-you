from decimal import Decimal
from shop.models import Product


class BasketService:
    @staticmethod
    def get_hardcoded_basket():
        basket_items = []
        total_price = Decimal('0.00')

        products = [
            {'id': 3, 'quantity': 1},
            {'id': 4, 'quantity': 3},
            {'id': 5, 'quantity': 2},
        ]

        for product_data in products:
            product = Product.objects.get(id=product_data['id'])
            item_total = product.price * product_data['quantity']

            basket_items.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': product_data['quantity'],
                'total': float(item_total),
            })
            total_price += item_total

        return basket_items, float(total_price)