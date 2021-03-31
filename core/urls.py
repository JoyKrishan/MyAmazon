from django.urls import path
from .views import item_listview, item_detailview, item_checkoutview
from .views import HomeView, ProductView, add_to_cart, remove_from_cart

urlpatterns = [
    path('', HomeView.as_view(), name="item_listview"),
    path('product/<slug:slug>/', ProductView.as_view(), name='item_detailview'),
    path('checkout/', item_checkoutview, name='item_checkout'),
    path('add-to-cart/<slug:slug>', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<slug:slug>', remove_from_cart, name='remove_from_cart')
]
# Built the product and checkout page
