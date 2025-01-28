class PurchaseService:
    @staticmethod
    def calculate_final_prices(basket_total):
        delivery_price = 7.0
        discount = 10.0
        total_after_discount = (basket_total + delivery_price) * (1 - discount / 100)

        return {
            'delivery_price': delivery_price,
            'discount': discount,
            'total_after_discount': round(total_after_discount, 2)
        }