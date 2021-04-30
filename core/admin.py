from django.contrib import admin
from .models import *


# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "ordered", "being_delivered", "received", "refund_requested", "refund_granted",
                    "billing_address", "payment", "coupon"]
    list_display_links = ["user", "billing_address", "payment", "coupon"]
    list_filter = ["ordered", "being_delivered", "received", "refund_requested", "refund_granted"]
    search_fields = ["user__username"]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["__str__", "get_total_each", "ordered"]


admin.site.register(Coupon)
admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(Refund)
