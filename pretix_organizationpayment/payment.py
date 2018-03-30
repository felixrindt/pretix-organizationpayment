import json
from collections import OrderedDict

from i18nfield.fields import I18nFormField, I18nTextarea
from i18nfield.strings import LazyI18nString

from pretix.base.payment import BasePaymentProvider
from pretix.base.models import RequiredAction
from pretix.base.templatetags.rich_text import rich_text
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django import forms

class OrganizationPayment(BasePaymentProvider):
    identifier = 'organizationpayment'

    @property
    def verbose_name(self):
        return str(self.settings.get('method_name', as_type=LazyI18nString)) or _('Organization')

    @property
    def orgafield_name(self):
        return self.settings.get('organizationfield_name', as_type=LazyI18nString) or _('Organization')

    @property
    def idfield_name(self):
        return self.settings.get('idfield_name', as_type=LazyI18nString) or _('Member ID')

    @property
    def information_text(self):
        return rich_text(self.settings.get('information_text', as_type=LazyI18nString))

    @property
    def payment_pending_text(self):
        return rich_text(self.settings.get('payment_pending_text', as_type=LazyI18nString))

    @property
    def payment_completed_text(self):
        return rich_text(self.settings.get('payment_completed_text', as_type=LazyI18nString))

    @property
    def organization_ids(self):
        l = self.settings.get('organizations_list')
        if not l:
            l = ""
        return [i.strip() for i in l.split('\n') if len(i) > 0]

    def payment_is_valid_session(self, request):
        return all([
            request.session.get('payment_%s_organization' % self.identifier, '') != '',
            request.session.get('payment_%s_memberID' % self.identifier, '') != '',
        ])

    def order_change_allowed(self, order):
        return False

    def payment_perform(self, request, order):
        organization = request.session.get('payment_%s_organization' % self.identifier, '')
        memberID = request.session.get('payment_%s_memberID' % self.identifier, '')
        order.payment_info = json.dumps({
            'organization': organization, 
            'memberID': memberID
        })
        order.save(update_fields=['payment_info'])
        RequiredAction.objects.create(
            event=order.event, action_type='pretix.plugins.organizationpayment.placed', data=json.dumps({
                'order': order.code,
            })
        )
        return None

    @property
    def settings_form_fields(self):
        name_field = I18nFormField(
            label = _('Payment method name'),
            help_text=_('Name of the payment method as shown to the user'),
            widget=I18nTextarea,
            widget_kwargs={'attrs': {'rows': '1'}},
        )
        organizationname_field = I18nFormField(
            label = _('Organization field annotation'),
            help_text = _('The annotation for the organization selection'),
            widget=I18nTextarea,
            widget_kwargs={'attrs': {'rows': '1'}},
        )
        idname_field = I18nFormField(
            label = _('ID field annotation'),
            help_text = _('The annotation of the field for the users ID string'),
            widget=I18nTextarea,
            widget_kwargs={'attrs': {'rows': '1'}},
        )
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
            help_text = _('Here you can provide a list of shorthand keys for all organizations you want to support. The short names should be alphanumeric and put on seperate lines. After saving you can set a display name and instructions for every organization. Be very careful about changing these.'),
            widget = forms.Textarea(attrs={'placeholder': 'BGW \nBGN \nUKMV \n...'}),
        )
        organizationlist = [
                ('method_name', name_field),
                ('organizationfield_name', organizationname_field),
                ('idfield_name', idname_field),
                ('information_text', info_field),
                ('payment_pending_text', pending_field),
                ('payment_completed_text', completed_field),
                ('organizations_list', organizations_field),
        ]
        for i in self.organization_ids:
            organizationlist.append(('organization_label_%s' % i, I18nFormField(
                label = _('Display name of %s') % i,
                help_text = _('The name of %s displayed to the user') % i,
                widget = I18nTextarea,
                widget_kwargs={'attrs': {
                    'rows': '1',
                    'placeholder': 'Organization ... (%s)' % i}},
            )))
            organizationlist.append(('organization_instructions_%s' % i, I18nFormField(
                label = _('Instructions for %s') % i,
                help_text = _('The message send to the user with instructions on how to complete the payment using the %s') % i,
                widget = I18nTextarea,
                widget_kwargs={'attrs': {
                    'placeholder': '1. Donwload the form from the %s \n2. Fill out the form \n3. Send the form to ...' % i}},
            )))

        return OrderedDict(list(super().settings_form_fields.items()) + organizationlist)

    @property
    def payment_form_fields(self):
        organization_name_field = ('organization',
            forms.ChoiceField(
            label=self.orgafield_name,
            required=True,
            choices=[(i, self.settings.get('organization_label_%s' % i, as_type=LazyI18nString)) for i in self.organization_ids]
        ))
        memberID_field = ('memberID',
            forms.CharField(
            label=self.idfield_name,
            required=True,
        ))
        return OrderedDict([
            organization_name_field,
            memberID_field,
        ])

    def payment_form_render(self, request):
        form = self.payment_form(request)
        template = get_template('pretix_organizationpayment/checkout_payment_form.html')
        ctx = {
                'request': request, 
                'form': form,
                'information_text': self.information_text,
        }
        return template.render(ctx)
    
    def checkout_confirm_render(self, request):
        template = get_template('pretix_organizationpayment/order.html')
        organization = request.session.get('payment_%s_organization' % self.identifier)
        ctx = {
            'information_text': self.information_text,
            'organization': self.settings.get('organization_label_%s' % organization, as_type=LazyI18nString),
            'memberID': request.session.get('payment_%s_memberID' % self.identifier),
            'instructions': self.settings.get('organization_instructions_%s' % organization, as_type=LazyI18nString),
            'orgafield_name': self.orgafield_name,
            'idfield_name': self.idfield_name,
        }
        return template.render(ctx)

    def order_pending_mail_render(self, order) -> str:
        template = get_template('pretix_organizationpayment/email.html')
        if 'payment_info' in json.loads(order.meta_info):
            payment_info = json.loads(order.meta_info)['payment_info']
        else:
            return _("No payment information available.")
        ctx = {
            'information_text': self.payment_pending_text,
            'organization': self.settings.get('organization_label_%s' % payment_info['organization'], as_type=LazyI18nString),
            'memberID': payment_info['memberID'],
            'instructions': self.settings.get('organization_instructions_%s' % payment_info['organization'], as_type=LazyI18nString),
            'orgafield_name': self.orgafield_name,
            'idfield_name': self.idfield_name,
        }
        return template.render(ctx)

    def order_pending_render(self, request, order) -> str:
        template = get_template('pretix_organizationpayment/order.html')
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            return _("No payment information available.")
        ctx = {
            'information_text': self.payment_pending_text,
            'organization': self.settings.get('organization_label_%s' % payment_info['organization'], as_type=LazyI18nString),
            'memberID': payment_info['memberID'],
            'instructions': self.settings.get('organization_instructions_%s' % payment_info['organization'], as_type=LazyI18nString),
            'orgafield_name': self.orgafield_name,
            'idfield_name': self.idfield_name,
        }
        return template.render(ctx)

    def order_completed_render(self, request, order) -> str:
        template = get_template('pretix_organizationpayment/order.html')
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            return _("No payment information available.")
        ctx = {
            'information_text': self.payment_completed_text,
            'organization': self.settings.get('organization_label_%s' % payment_info['organization'], as_type=LazyI18nString),
            'memberID': payment_info['memberID'],
            'instructions': self.settings.get('organization_instructions_%s' % payment_info['organization'], as_type=LazyI18nString),
            'orgafield_name': self.orgafield_name,
            'idfield_name': self.idfield_name,
        }
        return template.render(ctx)


    def order_control_render(self, request, order) -> str:
        template = get_template('pretix_organizationpayment/control.html')
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            return _("No payment information available.")
        ctx = {
            'organization': self.settings.get('organization_label_%s' % payment_info['organization'], as_type=LazyI18nString),
            'memberID': payment_info['memberID'],
            'orgafield_name': self.orgafield_name,
            'idfield_name': self.idfield_name,
            'method_name': self.verbose_name,
        }
        return template.render(ctx)
