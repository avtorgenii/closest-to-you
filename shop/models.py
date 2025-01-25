import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CharField, DecimalField, DateTimeField, ForeignKey, OneToOneField, TextField, IntegerField, \
    FileField, ImageField
from django.urls import reverse


# Users
class Client(models.Model):
    """Stores client information linked to user account with loyalty points."""
    phone_number = CharField(max_length=255, unique=True)
    loyalty_points = DecimalField(max_digits=10, decimal_places=2, default=0)
    compensations = DecimalField(max_digits=10, decimal_places=2, default=0)

    user = OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')

    def __str__(self):
        return f"Client: {self.user.first_name} {self.user.last_name} ({self.user.email})"


class WorkerRole(models.Model):
    """Contains possible worker roles (e.g., 'Support', 'Courier')."""
    name = CharField(max_length=255, unique=True)


class Worker(models.Model):
    """Stores worker information linked to user account with role and salary."""
    phone_number = CharField(max_length=15, unique=True)
    salary = DecimalField(max_digits=19, decimal_places=2)
    fire_date = DateTimeField(null=True, blank=True)

    role = ForeignKey(WorkerRole, on_delete=models.CASCADE,
                      related_name='workers')  # WorkerRole.objects.get(pk=1).workers.all() - returns all workers with that role
    user = OneToOneField(User, on_delete=models.CASCADE,
                         related_name='worker_profile')  # User.objects.get(pk=1).worker_profile goes from User to Worker

    def __str__(self):
        return f"Worker: {self.user.first_name} {self.user.last_name} ({self.role.name})"


# Product stuff
class VAT(models.Model):
    """Value Added Tax rates storage."""
    value = DecimalField(max_digits=5, decimal_places=2, unique=True)

    def __str__(self):
        return f"{self.value}%"


class ProductCategory(models.Model):
    """Product categorization system."""
    name = CharField(max_length=255)


class Product(models.Model):
    """Main product model with pricing, discounts, and age restrictions."""
    name = CharField(max_length=255)
    description = TextField(null=True, blank=True)
    price = DecimalField(max_digits=19, decimal_places=2)
    image = ImageField(upload_to='products/', default=None, blank=True, null=True)
    discount = DecimalField(max_digits=5, decimal_places=2) # not as percents, but as 0.2 and 0.05 an etc
    above_18_years = models.BooleanField(default=False)

    category = ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    vat = ForeignKey(VAT, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Order(models.Model):
    """Client order containing multiple products and delivery information."""
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2)

    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField('Product', through='OrderProduct', related_name='orders')

    def __str__(self):
        return f"Order {self.id} by {self.client}"

    def update_total_price(self, *args, **kwargs):
        """Recalculates order total including product discounts and delivery cost."""
        # Calculate total price from products, considering the discount
        total_product_price = sum(
            order_product.product.price * (1 - order_product.product.discount / 100) * order_product.quantity
            for order_product in self.order_products.all()
        )

        # Update the total price based on the product prices and the delivery price
        self.total_price = total_product_price + self.delivery_price

        # Save the order after updating the total price
        super(Order, self).save(*args, **kwargs)



class OrderProduct(models.Model):
    """Linking table for products in orders with quantities."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"


# Delivery stuff
class Address(models.Model):
    """Delivery address storage with city/street/house details."""
    city = CharField(max_length=255)
    street = CharField(max_length=255, null=True, blank=True)
    house_number = CharField(max_length=255)
    apartment_number = IntegerField(null=True, blank=True)
    postal_code = CharField(max_length=25)

    def __str__(self):
        return f"{self.city}, {self.street} {self.house_number}/{self.apartment_number}" if self.apartment_number else f"{self.city}, {self.street} {self.house_number}"


class DeliveryLeavePlace(models.Model):
    """Physical locations where couriers can leave orders."""
    name = CharField(max_length=255, unique=True)


class DeliveryStage(models.Model):
    """Delivery status stages (e.g., 'Preparing', 'In Transit')."""
    name = CharField(max_length=255, unique=True)


class Delivery(models.Model):
    """Delivery information linking orders to couriers and addresses."""
    planned_time = DateTimeField()
    arrived_time = DateTimeField(null=True, blank=True)

    order = OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    deliverer = ForeignKey(Worker, null=True, blank=True, on_delete=models.CASCADE, related_name='deliveries')
    address = ForeignKey(Address, on_delete=models.CASCADE)
    delivery_leave_place = ForeignKey(DeliveryLeavePlace, on_delete=models.CASCADE)
    delivery_stage = ForeignKey(DeliveryStage, on_delete=models.CASCADE, default=1)

    def get_absolute_url(self):  # used in templates to generate redirect url which will be handled in views
        return reverse('delivery', kwargs={'d_id': self.pk})


class PaymentType(models.Model):
    """Payment method options (e.g., 'Credit Card', 'Cash')."""
    name = CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    """Payment records linked to specific orders."""
    id = models.CharField(
        max_length=36,  # The length of a UUID or your custom ID format
        primary_key=True,
        default=uuid.uuid4,  # Generates a random UUID
        editable=False
    )

    payment_type = ForeignKey(PaymentType, on_delete=models.CASCADE)
    order = ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"Payment for Order {self.order.id}"


class ComplaintType(models.Model):
    """Types of possible complaints (e.g., 'Late Delivery', 'Damaged Goods')."""
    name = CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    """Client complaint submission model, linking client, order and support_worker. Complaint comes with attachment and resolution."""
    title = CharField(max_length=255)
    description = TextField(null=False, blank=False)
    attachment = FileField(upload_to='complaints/', null=True, blank=True)
    submission_date = DateTimeField(auto_now_add=True)
    resolution_date = DateTimeField(null=True, blank=True)
    resolution = TextField(null=True, blank=True)

    complaint_type = ForeignKey(ComplaintType, on_delete=models.CASCADE)
    client = ForeignKey(Client, on_delete=models.CASCADE)
    worker = ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)
    order = ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):  # used in templates to generate redirect url which will be handled in views
        return reverse('complaint', kwargs={'c_id': self.pk})


class Incident(models.Model):
    """Records delivery incidents with compensations and final resolution of incident."""
    date = DateTimeField(auto_now_add=True)
    description = TextField(null=True, blank=True)
    deliverer_compensation = DecimalField(max_digits=10, decimal_places=2, default=0)
    resolution = TextField(null=True, blank=True)

    deliverer = ForeignKey(Worker, on_delete=models.CASCADE, related_name='deliverer_incidents')
    delivery = ForeignKey(Delivery, on_delete=models.CASCADE, related_name='incidents')
    support_worker = ForeignKey(Worker, on_delete=models.CASCADE, related_name='support_worker_incidents')

    def __str__(self):
        return f"Incident on {self.date} reported by {self.deliverer}"
