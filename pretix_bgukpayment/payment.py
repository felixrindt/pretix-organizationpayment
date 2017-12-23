import json
from collections import OrderedDict

from i18nfield.fields import I18nFormField, I18nTextarea
from i18nfield.strings import LazyI18nString

from pretix.base.payment import BasePaymentProvider
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django import forms

class BGUKPayment(BasePaymentProvider):
    identifier = 'bgukpayment'
    verbose_name =_('BG/UK Payment')

    def checkout_prepare(self, request, total):
        return True

    def payment_is_valid_session(self, request):
        return True

    def order_change_allowed(self, order):
        return False

    def checkout_prepare(self, request, total):
        return True

    def payment_is_valid_session(self, request):
        return True

    def checkout_confirm_render(self, request):
        return self.payment_form_render(request)
    
    @property
    def settings_form_fields(self):
        info_field = I18nFormField(
            label = _('Payment information text'),
            help_text=_('Shown to the user when selecting a payment method.'),
            widget = I18nTextarea,
        )
        pending_field = I18nFormField(
            label = _('Payment pending text'),
            help_text = _('Shown to the user when viewing a pending payment order.'),
            widget = I18nTextarea,
        )
        completed_field = I18nFormField(
            label = _('Payment completed text'),
            help_text = _('Shown to the user when viewing an order with completed payment.'),
            widget = I18nTextarea,
        )
        return OrderedDict(list(super().settings_form_fields.items()) + [
                ('information_text', info_field),
                ('payment_pending_text', pending_field),
                ('payment_completed_text', completed_field),
            ])

    @property
    def payment_form_fields(self):
        bgukName_field = ('bguk',
            forms.ChoiceField(
            label=_('Organization'),
            help_text=_('Name of your Berufsgenossenschaft oder \'Unfallkasse\'.'),
            required=True,
            choices=(
                ("BGW", "Berufsgenossenschaft Wohlfahrt"),
                ("UK", "Unfallkasse"),
                ("other", "Andere Berufsgenossenschaften"),
            ),
        ))
        memberID_field = ('memberID',
            forms.CharField(
            label=_('Member ID'),
            help_text=_('Your member ID at the BG/UK.'),
            required=True,
        ))
        return OrderedDict([
            bgukName_field,
            memberID_field,
        ])

    def checkout_prepare(self, request, cart):
        form = self.payment_form(request)
        if form.is_valid():
            request.session['payment_bgukpayment_bguk'] = form.cleaned_data['bguk']
            request.session['payment_bgukpayment_memberID'] = form.cleaned_data['memberID']
            return True
        return False


    def payment_form_render(self, request):
        form = self.payment_form(request)
        template = get_template('pretix_bgukpayment/checkout_payment_form.html')
        ctx = {
                'request': request, 
                'form': form,
                'information_text': self.settings.get('information_text', as_type=LazyI18nString),
        }
        return template.render(ctx)
    
    def checkout_confirm_render(self, request):
        template = get_template('pretix_bgukpayment/checkout_confirm.html')
        ctx = {
            'request': request,
            'event': self.event,
            'information_text': self.settings.get('information_text', as_type=LazyI18nString),
            'bguk': request.session.get('payment_bgukpayment_bguk'),
            'memberID': request.session.get('payment_bgukpayment_memberID'),
        }
        return template.render(ctx)

    def order_pending_mail_render(self, order) -> str:
        template = get_template('pretix_bgukpayment/email/order_pending.txt')
        ctx = {
            'event': self.event,
            'order': order,
            'information_text': self.settings.get('information_text', as_type=LazyI18nString),
        }
        return template.render(ctx)

    def order_pending_render(self, request, order) -> str:
        template = get_template('pretix_bgukpayment/pending.html')
        ctx = {
            'event': self.event,
            'order': order,
            'information_text': self.settings.get('payment_pending_text', as_type=LazyI18nString),
        }
        return template.render(ctx)

    def order_completed_render(self, request, order) -> str:
        template = get_template('pretix_bgukpayment/pending.html')
        ctx = {
            'event': self.event,
            'order': order,
            'information_text': self.settings.get('payment_completed_text', as_type=LazyI18nString),
        }
        return template.render(ctx)


    def order_control_render(self, request, order) -> str:
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            payment_info = None
        template = get_template('pretix_bgukpayment/control.html')
        ctx = {'request': request, 'event': self.event,
               'payment_info': payment_info, 
               'order': order,
               'bguk': request.session.get('payment_bgukpayment_bguk'),
               'memberID': request.session.get('payment_bgukpayment_memberID'),
        }
        return template.render(ctx)
