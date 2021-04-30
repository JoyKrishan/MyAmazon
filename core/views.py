from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon, Refund
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm
import stripe
import string, random

stripe.api_key = settings.STRIPE_API_KEY


# helper functions

def ref_code_generator():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


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


def get_billing_address(request):
    try:
        billing_address = BillingAddress.objects.get(user=request.user)
        return billing_address
    except ObjectDoesNotExist:
        return None


class CheckoutView(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        form = CheckoutForm(instance=get_billing_address(self.request))
        coupon_form = CouponForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have a active order")
            return redirect()
        context = {
            "order": order,
            "form": form,
            "coupon_form": coupon_form,
        }
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None, instance=get_billing_address(self.request))
        print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get("street_address")
                apartment_address = form.cleaned_data.get("apartment_address")
                zip_code = form.cleaned_data.get("zip_code")
                country = form.cleaned_data.get("country")
                # TODO: Add functionalities
                # shipping_address = form.cleaned_data.get("shipping_address")
                # save_info = form.cleaned_data.get("save_info")
                payment_method = form.cleaned_data.get("payment_method")

                billing_address, created = BillingAddress.objects.get_or_create(user=self.request.user)
                billing_address.street_address = street_address
                billing_address.zip_code = zip_code
                billing_address.country = country
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                messages.success(self.request, "Billing address saved")
                if payment_method == 'S':
                    return redirect('payment_view', payment_method='stripe')
                elif payment_method == 'P':
                    return redirect('payment_view', payment_method='paypal')
                else:
                    messages.warning(self.request, "Invalid Parameters")
                    return redirect('checkout')
            else:
                messages.warning(self.request, "Error in the post form")
            return redirect("checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("order_summary")


class PaymentView(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            billing_address = get_billing_address(self.request)
            if not billing_address:
                messages.warning(self.request, "Please add the billing address first")
                return redirect("checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("order_summary")
        context = {
            'order': order,
            "STRIPE_API_KEY": "pk_test_TYooMQauvdEDq54NiTphI7jx"
        }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            amount = int(order.get_total() * 100)  # converted to cents
            try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=self.request.POST['stripeToken'],
                    description="My First Test Charge (created for API docs)",
                )
                # print(charge)
                payment = Payment()
                payment.charge_id = charge.get("id")
                payment.user = self.request.user
                payment.amount = amount
                payment.save()
                order.payment = payment
                # Here the payment was successful
                ref_code = ref_code_generator()
                order.ref_code = ref_code
                order.ordered = True
                # update all the orderItems
                for order_item in order.items.all():
                    order_item.ordered = True
                    order_item.save()
                order.save()
                messages.success(self.request, "Order successfully placed")
                return redirect("/")
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught

                # print('Status is: %s' % e.http_status)
                # print('Code is: %s' % e.code)
                # param is '' in this case
                # print('Param is: %s' % e.param)
                # print('Message is: %s' % e.user_message)
                messages.warning(self.request, f"ERROR: {e.user_message}, ERR_Code: {e.code}")
                return redirect("/")
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "")
                return redirect("/")
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Authentication with Stripe's API failed")
                return redirect("/")
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Poor Network")
                return redirect("/")
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(self.request, "Generic Error")
                return redirect("/")
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                print(e)
                print(self.request.POST)
                messages.warning(self.request, "Something happened unrelated to Stripe")
                return redirect("/")

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
        return render(self.request, "payment.html")


class HomeView(ListView):
    model = Item
    paginate_by = 2
    template_name = 'home-page.html'


class ProductView(DetailView):
    model = Item
    template_name = 'product-page.html'


class OrderSummary(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                "order": order
            }
            return render(self.request, "order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("order_summary.html")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)  # for multiple orders
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
            return redirect("order_summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item is added to the cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item is added to the cart")

    return redirect("item_detailview", slug=slug)


@login_required
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


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # if such a order already exists means the orderItem was created
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 0:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "The item is removed")
    return redirect("order_summary")


def get_coupon(code, request):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, f"There is no {code} coupon")
        return None


class AddCoupon(View, LoginRequiredMixin):
    def post(self, *args, **kwargs):
        # Coupon form to get the coupon code
        print("HERE")
        form = CouponForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                code = form.cleaned_data.get("code")
                coupon = get_coupon(code, self.request)
                if coupon:
                    order.coupon = coupon
                    order.save()
                    messages.success(self.request, "Successfully added coupon")
                    return redirect("checkout")

                else:
                    return redirect("checkout")

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("order_summary.html")


@login_required
def ordered_view(request):
    order_qs = Order.objects.filter(user=request.user, ordered=True)
    if order_qs.exists():
        context = {
            "order_qs": order_qs
        }
        return render(request, "ordered_view.html", context)

    else:
        messages.warning(request, "You did not place any order")
        return redirect("/")


class RefundView(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        refund_form = RefundForm()
        context = {
            "form": refund_form
        }
        return render(self.request, "refund_view.html", context)

    def post(self, *args, **kwargs):
        refund_form = RefundForm(self.request.POST or None)
        print(self.request.POST)
        if refund_form.is_valid():
            email = refund_form.cleaned_data.get("email")
            ref_code = refund_form.cleaned_data.get("ref_code")
            reason = refund_form.cleaned_data.get("reason")
            try:
                order = Order.objects.get(ref_code=ref_code)
                refund = Refund()
                refund.reason = reason
                refund.order = order
                refund.accepted = True
                refund.save()
                order.refund_requested = True
                order.save()
                messages.success(self.request, "Your request has been accepted")

            except ObjectDoesNotExist:
                messages.warning(self.request, "You do not have an order with such reference code")

        return redirect("/")
