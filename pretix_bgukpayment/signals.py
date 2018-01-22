# Register your receivers here
from django.dispatch import receiver

from pretix.base.signals import register_payment_providers
from pretix.presale.signals import order_meta_from_request

@receiver(register_payment_providers, dispatch_uid="payment_bguk.provider")
def register_payment_provider(sender, **kwargs):
    from .payment import BGUKPayment
    return BGUKPayment

@receiver(order_meta_from_request, dispatch_uid="payment_bguk.order_meta")
def register_order_meta(sender, request, **kwargs):
    from .payment import BGUKPayment
    bguk = request.session.get('payment_%s_bguk' % BGUKPayment.identifier, '')
    memberID = request.session.get('payment_%s_memberID' % BGUKPayment.identifier, '')
    if not bguk and not memberID:
        return {'payment_info': {
            'bguk': bguk,
            'memberID': memberID
        }}
    return {}
