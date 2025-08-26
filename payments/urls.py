from django.urls import path
from .views import create_checkout_session, stripe_webhook

urlpatterns = [
    path('payments/checkout-session/', create_checkout_session, name='payments-checkout'),
    path('payments/stripe/webhook/', stripe_webhook, name='payments-webhook'),
]


