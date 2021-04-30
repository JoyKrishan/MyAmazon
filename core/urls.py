from django.urls import path
from .views import item_listview, item_detailview, CheckoutView, PaymentView, AddCoupon, ordered_view, RefundView
from .views import HomeView, ProductView, add_to_cart, remove_from_cart, OrderSummary, remove_single_item_from_cart

urlpatterns = [
    path('', HomeView.as_view(), name="item_listview"),
    path('product/<slug:slug>/', ProductView.as_view(), name='item_detailview'),
    path('payment/<payment_method>', PaymentView.as_view(), name='payment_view'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug:slug>', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<slug:slug>', remove_from_cart, name='remove_from_cart'),
    path('order-summary', OrderSummary.as_view(), name='order_summary'),
    path('remove-item-from-cart/<slug:slug>', remove_single_item_from_cart, name='remove_item_from_cart'),
    path('addCoupon/', AddCoupon.as_view(), name='add_coupon'),
    path('ordered/', ordered_view, name="ordered_view"),
    path("request-refund/", RefundView.as_view(), name="refund_view")
]
# Built the product and checkout page
