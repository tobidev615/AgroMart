import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from orders.models import Order
from .models import Payment, PaymentStatus
from .models import Wallet
from .serializers import (
    WalletSerializer,
    WalletDepositSerializer,
    PaymentSerializer,
)
from .services import wallet_deposit, pay_order_from_wallet, ensure_wallet


@api_view(["POST"]) 
@permission_classes([permissions.IsAuthenticated])
def create_checkout_session(request):
    order_id = request.data.get('order_id')
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=404)

    stripe.api_key = settings.STRIPE_API_KEY
    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f'Order #{order.id}'},
                'unit_amount': int(order.total_amount * 100),
            },
            'quantity': 1,
        }],
        success_url='https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://example.com/cancel',
        metadata={'order_id': str(order.id), 'user_id': str(request.user.id)},
    )

    Payment.objects.update_or_create(
        order=order,
        defaults={
            'user': request.user,
            'amount': order.total_amount,
            'currency': 'usd',
            'provider_payment_id': session.id,
            'status': PaymentStatus.PENDING,
        }
    )
    return Response({"checkout_session_id": session.id, "checkout_url": session.url})


@csrf_exempt
@api_view(["POST"]) 
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        data = event['data']['object']
        order_id = data['metadata'].get('order_id')
        provider_payment_id = data['id']
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(status=200)
        Payment.objects.filter(order=order).update(status=PaymentStatus.SUCCEEDED, provider_payment_id=provider_payment_id)
        # generate invoice PDF (temporarily disabled)
        # html = HTML(string=f"<h1>Invoice</h1><p>Order #{order.id} - Amount: {order.total_amount}</p>")
        # pdf_io = io.BytesIO()
        # html.write_pdf(pdf_io)
        # pdf_io.seek(0)
        # invoice = Invoice.objects.create(user=order.user, order=order)
        # invoice.file.save(f"invoice_{order.id}.pdf", pdf_io)
    return Response(status=200)


@api_view(["GET"]) 
@permission_classes([permissions.IsAuthenticated])
def wallet_detail(request):
    wallet = ensure_wallet(request.user)
    return Response(WalletSerializer(wallet).data)


@api_view(["POST"]) 
@permission_classes([permissions.IsAuthenticated])
def wallet_deposit_view(request):
    serializer = WalletDepositSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    amount = serializer.validated_data["amount"]
    reference = serializer.validated_data.get("reference", "")
    tx = wallet_deposit(request.user, amount, reference, metadata={"source": "api"})
    wallet = tx.wallet
    return Response({"wallet": WalletSerializer(wallet).data}, status=status.HTTP_201_CREATED)


@api_view(["POST"]) 
@permission_classes([permissions.IsAuthenticated])
def pay_order_with_wallet(request):
    order_id = request.data.get("order_id")
    if not order_id:
        return Response({"detail": "order_id is required"}, status=400)
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=404)
    payment = pay_order_from_wallet(request.user, order, amount=None)
    return Response(PaymentSerializer(payment).data, status=200)