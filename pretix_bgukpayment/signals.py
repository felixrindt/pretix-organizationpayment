# Register your receivers here
from django.dispatch import receiver

from pretix.base.signals import register_payment_providers

@receiver(register_payment_providers, dispatch_uid="payment_bguk")
def register_payment_provider(sender, **kwargs):
    from .payment import BGUKPayment
    return BGUKPayment
