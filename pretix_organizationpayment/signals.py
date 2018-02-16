# Register your receivers here
from django.dispatch import receiver

from pretix.base.signals import register_payment_providers
from pretix.presale.signals import order_meta_from_request

@receiver(register_payment_providers, dispatch_uid="payment_organization.provider")
def register_payment_provider(sender, **kwargs):
    from .payment import OrganizationPayment
    return OrganizationPayment

@receiver(order_meta_from_request, dispatch_uid="payment_organization.order_meta")
def register_order_meta(sender, request, **kwargs):
    from .payment import OrganizationPayment
    organization = request.session.get('payment_%s_organization' % OrganizationPayment.identifier, '')
    memberID = request.session.get('payment_%s_memberID' % OrganizationPayment.identifier, '')
    if not organization and not memberID:
        return {'payment_info': {
            'organization': organization,
            'memberID': memberID
        }}
    return {}
