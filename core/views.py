from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import HttpResponse
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView
from django.utils import timezone


# Create your views here.

def item_listview(request):
    items = Item.objects.all()
    context = {
        "items": items
    }
    return render(request, "home-page.html", context)


def item_detailview(request):
    # items = Item.objects.get(id=1)
    # context = {
    #   "item":item
    # }
    return render(request, "product-page.html")


def item_checkoutview(request):
    return render(request, "checkout-page.html")


# Class Based Views

class HomeView(ListView):
    model = Item
    paginate_by = 2
    template_name = 'home-page.html'


class ProductView(DetailView):
    model = Item
    template_name = 'product-page.html'


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        # print("Here is the type {}".format(type(order.items)))
        # print("Here is all the "
        #     "functions that are available in te class")
        # print(dir(order.items))
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item is updated in the cart")
        else:
            order.items.add(order_item)
            messages.info(request, "Item is added to the cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(OrderItem)
        messages.info(request, "Item is added to the cart")

    return redirect("item_detailview", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # if such a order already exists means the orderItem was created
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)
            order.items.remove(order_item[0])
            order_item.delete()
            messages.info(request, "Item is removed from the cart")
        else:
            # Show a message to the user that the product was not added
            messages.info(request, "Item is not added to the cart")
            return redirect("item_detailview", slug=slug)
    else:
        messages.info(request, "There is no order")
    return redirect("item_detailview", slug=slug)
