import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
# from weasyprint import HTML  # Disabled due to system dependency issues

from orders.models import Order
from .models import Payment, PaymentStatus
# from .models import Invoice  # Temporarily disabled


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
