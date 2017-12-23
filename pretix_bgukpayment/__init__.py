from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class PluginApp(AppConfig):
    name = 'pretix_bgukpayment'
    verbose_name = 'Berufsgenossenschaft/Unfallkasse Payment Provider'

    class PretixPluginMeta:
        name = ugettext_lazy('Berufsgenossenschaft/Unfallkasse Payment Provider')
        author = 'Felix Rindt'
        description = ugettext_lazy('This pretix plugin adds a payment provider for german Be')
        visible = True
        version = '1.0.0'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_bgukpayment.PluginApp'
