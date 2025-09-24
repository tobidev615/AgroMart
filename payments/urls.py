from django.urls import path
from .views import (
    create_checkout_session,
    stripe_webhook,
    wallet_detail,
    wallet_deposit_view,
    pay_order_with_wallet,
)

urlpatterns = [
    path('payments/checkout-session/', create_checkout_session, name='payments-checkout'),
    path('payments/stripe/webhook/', stripe_webhook, name='payments-webhook'),
    path('payments/wallet/', wallet_detail, name='wallet-detail'),
    path('payments/wallet/deposit/', wallet_deposit_view, name='wallet-deposit'),
    path('payments/wallet/pay/', pay_order_with_wallet, name='wallet-pay-order'),
]


