import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CharField, DecimalField, DateTimeField, ForeignKey, OneToOneField, TextField, IntegerField, \
    FileField, ImageField


# Users
class Client(models.Model):
    phone_number = CharField(max_length=255, unique=True)
    loyalty_points = DecimalField(max_digits=10, decimal_places=2, default=0)

    user = OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')

    def __str__(self):
        return f"Client: {self.user.first_name} {self.user.last_name} ({self.user.email})"


class WorkerRole(models.Model):
    name = CharField(max_length=255, unique=True)


class Worker(models.Model):
    phone_number = CharField(max_length=15, unique=True)
    salary = DecimalField(max_digits=19, decimal_places=2)
    fire_date = DateTimeField(null=True, blank=True)

    role = ForeignKey(WorkerRole, on_delete=models.CASCADE,
                      related_name='workers')  # WorkerRole.objects.get(pk=1).workers.all() - returns all workers with that role
    user = OneToOneField(User, on_delete=models.CASCADE,
                         related_name='worker_profile')  # User.objects.get(pk=1).worker_profile goes from User to Worker

    def __str__(self):
        return f"Worker: {self.user.first_name} {self.user.last_name} ({self.role})"


# Product stuff
class VAT(models.Model):
    value = DecimalField(max_digits=5, decimal_places=2, unique=True)

    def __str__(self):
        return f"{self.value}%"

class ProductCategory(models.Model):
    name = CharField(max_length=255)

class Product(models.Model):
    name = CharField(max_length=255)
    description = TextField(null=True, blank=True)
    price = DecimalField(max_digits=19, decimal_places=2)
    image = ImageField(upload_to='products/', default=None, blank=True, null=True)
    discount = DecimalField(max_digits=5, decimal_places=2)
    above_18_years = models.BooleanField()

    category = ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    vat = ForeignKey(VAT, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Order(models.Model):
    order_date = DateTimeField(auto_now_add=True)
    total_price = DecimalField(max_digits=10, decimal_places=2)
    delivery_price = DecimalField(max_digits=10, decimal_places=2)

    client = ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} by {self.client}"


# Delivery stuff
class Address(models.Model):
    city = CharField(max_length=255)
    street = CharField(max_length=255, null=True, blank=True)
    house_number = CharField(max_length=255)
    apartment_number = IntegerField(null=True, blank=True)
    postal_code = CharField(max_length=25)

    def __str__(self):
        return f"{self.city}, {self.street} {self.house_number}/{self.apartment_number}" if self.apartment_number else f"{self.city}, {self.street} {self.house_number}"


class DeliveryLeavePlace(models.Model):
    name = CharField(max_length=255, unique=True)


class Delivery(models.Model):
    delivery_date = DateTimeField()

    order = ForeignKey(Order, on_delete=models.CASCADE)
    address = ForeignKey(Address, on_delete=models.CASCADE)
    delivery_leave_place = ForeignKey(DeliveryLeavePlace, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.delivery_date} by {self.order}"


class PaymentType(models.Model):
    name = CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
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
    name = CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    title = CharField(max_length=255)
    description = TextField(null=False, blank=False)
    attachment = FileField(upload_to='complaints/', null=True, blank=True)
    submission_date = DateTimeField(auto_now_add=True)
    resolution_date = DateTimeField(null=True, blank=True)
    resolution = TextField(null=True, blank=True)

    complaint_type = ForeignKey(ComplaintType, on_delete=models.CASCADE)
    client = ForeignKey(Client, on_delete=models.CASCADE)
    worker = ForeignKey(Worker, on_delete=models.CASCADE)
    order = ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Incident(models.Model):
    date = DateTimeField(auto_now_add=True)
    description = TextField()
    deliverer_compensation = DecimalField(max_digits=10, decimal_places=2)
    resolution = TextField(null=True, blank=True)

    deliverer = ForeignKey(Worker, on_delete=models.CASCADE, related_name='deliverer')
    support_worker = ForeignKey(Worker, on_delete=models.CASCADE, related_name='support_worker')

    def __str__(self):
        return f"Incident on {self.date} reported by {self.deliverer}"
