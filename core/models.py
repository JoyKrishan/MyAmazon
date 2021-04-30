from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

# Create your models here.
CATEGORY_CHOICES = [
    ('S', "Shirt"),  # (what goes into DB, Shown text)
    ('SW', "Sports wears"),
    ('OW', "Outwears")
]

LABEL_CHOICES = [
    ('P', "primary"),  # (what goes into DB, Shown text)
    ('S', "secondary"),
    ('D', "danger")
]


class Item(models.Model):
    title = models.CharField(max_length=100, blank=False, default="No Title Added")
    price = models.FloatField(max_length=3, default=0.00, blank=False)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, blank=False, default='S')
    label = models.CharField(max_length=1, choices=LABEL_CHOICES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    discount_price = models.FloatField(max_length=3, blank=True, null=True)
    slug = models.SlugField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('item_detailview', kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
        return self.item.price * self.quantity

    def get_total_item_discount_price(self):
        return self.item.discount_price * self.quantity

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_item_discount_price()

    def get_total_each(self):
        if self.item.discount_price:
            return self.get_total_item_discount_price()
        else:
            return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    # Adding the status after the product is successfully ordered
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for item in self.items.all():
            total = total + item.get_total_each()
        if self.coupon:
            total -= self.coupon.amount
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=6)
    country = CountryField(multiple=False)
    shipping_address = models.BooleanField(blank=True, null=True)
    save_info = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    charge_id = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount}BDT On {str(self.timestamp).split(' ')[0]}"


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.order
