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
    verbose_name = _('BG/UK Payment')

    def bguk_ids(self):
        l = self.settings.get('organizations_list')
        if not l:
            l = ""
        return [i.strip() for i in l.split('\n') if len(i) > 0]

    def payment_is_valid_session(self, request):
        if not request.session.get('payment_%s_bguk' % self.identifier):
            return False
        if not request.session.get('payment_%s_memberID' % self.identifier):
            return False
        return True

    def order_change_allowed(self, order):
        return False

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
        organizations_field = forms.CharField(
            label = _('Organizations'),
            help_text = _('Here you can provice a list of shorthand keys for all organizations you want to support. The short names should be alphanumeric and put on seperate lines. After saving you can set a display name and instructions for every organization. Be very careful about changing these.'),
            widget = forms.Textarea(attrs={'placeholder': 'BGW\nBGN\nUKMV\n...'}),
        )
        bguklist = [
                ('information_text', info_field),
                ('payment_pending_text', pending_field),
                ('payment_completed_text', completed_field),
                ('organizations_list', organizations_field),
        ]
        for i in self.bguk_ids():
            bguklist.append(('bguk_label_%s' % i, I18nFormField(
                label = _('Display name of %s' % i),
                help_text = _('The name of %s displayed to the user' % i),
                widget = I18nTextarea,
                widget_kwargs={'attrs': {
                    'rows': '1',
                    'placeholder': 'Berufsgenossenschaft ... (%s)' % i}},
            )))
            bguklist.append(('bguk_instructions_%s' % i, I18nFormField(
                label = _('Instructions for %s' % i),
                help_text = _('The message send to the user with instructions on how to complete the payment using the %s' % i),
                widget = I18nTextarea,
                widget_kwargs={'attrs': {
                    'placeholder': '1. Donwload the form from the %s\n2. Fill out the form\n3. Send the form to ...' % i}},
            )))

        return OrderedDict(list(super().settings_form_fields.items()) + bguklist)

    @property
    def payment_form_fields(self):
        bgukName_field = ('bguk',
            forms.ChoiceField(
            label=_('Organization'),
            help_text=_('Name of your organization'),
            required=True,
            choices=[(i, self.settings.get('bguk_label_%s' % i, as_type=LazyI18nString)) for i in self.bguk_ids()]
        ))
        memberID_field = ('memberID',
            forms.CharField(
            label=_('Member ID'),
            help_text=_('Your member ID at that organization'),
            required=True,
        ))
        return OrderedDict([
            bgukName_field,
            memberID_field,
        ])

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
        bguk = request.session.get('payment_%s_bguk' % self.identifier)
        ctx = {
            'request': request,
            'event': self.event,
            'information_text': self.settings.get('information_text', as_type=LazyI18nString),
            'bguk': self.settings.get('bguk_label_%s' % bguk, as_type=LazyI18nString),
            'memberID': request.session.get('payment_%s_memberID' % self.identifier),
            'instructions': self.settings.get('bguk_instructions_%s' % bguk, as_type=LazyI18nString),
        }
        print("bguk======================",bguk)
        print(ctx)
        return template.render(ctx)

    def order_pending_mail_render(self, order) -> str:
        template = get_template('pretix_bgukpayment/email/order_pending.txt')
        ctx = {
            'event': self.event,
            'order': order,
            'information_text': self.settings.get('information_text', as_type=LazyI18nString),
            'bguk': self.settings.get('bguk_label_%s' % bguk, as_type=LazyI18nString),
            'memberID': request.session.get('payment_bgukpayment_memberID'),
            'instructions': self.settings.get('bguk_instructions_%s' % bguk, as_type=LazyI18nString),
        }
        return template.render(ctx)

    def order_pending_render(self, request, order) -> str:
        template = get_template('pretix_bgukpayment/pending.html')
        ctx = {
            'event': self.event,
            'order': order,
            'information_text': self.settings.get('payment_pending_text', as_type=LazyI18nString),
            'bguk': self.settings.get('bguk_label_%s' % bguk, as_type=LazyI18nString),
            'memberID': request.session.get('payment_bgukpayment_memberID'),
            'instructions': self.settings.get('bguk_instructions_%s' % bguk, as_type=LazyI18nString),
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
               'bguk': request.session.get('payment_%s_bguk' % self.identifier),
               'memberID': request.session.get('payment_%s_memberID' % self.identifier),
        }
        return template.render(ctx)
