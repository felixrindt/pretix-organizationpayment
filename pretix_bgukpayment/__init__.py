from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class PluginApp(AppConfig):
    name = 'pretix_bgukpayment'
    verbose_name = 'Organization Payment Provider'

    class PretixPluginMeta:
        name = ugettext_lazy('Organization Payment Provider')
        author = 'Felix Rindt'
        description = ugettext_lazy('This pretix plugin adds a payment provider for organizations like the german Berufsgenossenschaft or Unfallkasse. It lets the user select an organization and asks for a member ID. You can define texts displayed to the user as well as the organizations you want to support with seperate instruction text for each of them.')
        visible = True
        restricted = False
        version = '1.0.0'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_bgukpayment.PluginApp'
