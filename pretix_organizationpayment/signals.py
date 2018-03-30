from django.dispatch import receiver

from pretix.base.signals import register_payment_providers, requiredaction_display
from pretix.presale.signals import order_meta_from_request
import json
from django.template.loader import get_template

@receiver(register_payment_providers, dispatch_uid="payment_organization.provider")
def register_payment_provider(sender, **kwargs):
    from .payment import OrganizationPayment
    return OrganizationPayment

@receiver(order_meta_from_request, dispatch_uid="payment_organization.order_meta")
def register_order_meta(sender, request, **kwargs):
    from .payment import OrganizationPayment
    organization = request.session.get('payment_%s_organization' % OrganizationPayment.identifier, '')
    memberID = request.session.get('payment_%s_memberID' % OrganizationPayment.identifier, '')
    if organization and memberID:
        return {'payment_info': {
            'organization': organization,
            'memberID': memberID
        }}
    return {}

@receiver(requiredaction_display, dispatch_uid="organizationpayment_requiredaction_display")
def pretixcontrol_action_display(sender, action, request, **kwargs):
    from .payment import OrganizationPayment
    if not action.action_type.startswith('pretix.plugins.organizationpayment.placed'):
        return
    data = json.loads(action.data)
    template = get_template('pretix_organizationpayment/requiredaction.html')
    pp = sender.get_payment_providers().get(OrganizationPayment.identifier)
    ctx = {'order': data['order'], 'event': sender, 'name': pp.verbose_name}
    return template.render(ctx, request)

