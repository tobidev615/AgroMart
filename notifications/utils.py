from typing import Optional

from django.core.mail import send_mail
from django.conf import settings

from .models import Notification


def _send_sms(phone_number: Optional[str], body: str) -> None:
    if not phone_number:
        return
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_number = getattr(settings, "TWILIO_FROM_NUMBER", None)
    if not (account_sid and auth_token and from_number):
        return
    try:
        from twilio.rest import Client  # type: ignore

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=body,
            from_=from_number,
            to=phone_number,
        )
    except Exception:
        # Fail silently in dev
        pass


def notify_user(user, title: str, message: str, email: bool = True, sms: bool = True):
    Notification.objects.create(user=user, title=title, message=message)
    if email and user.email:
        send_mail(subject=title, message=message, from_email=None, recipient_list=[user.email])
    if sms:
        phone_number = getattr(getattr(user, "profile", None), "phone_number", None)
        _send_sms(phone_number, f"{title}: {message}")


