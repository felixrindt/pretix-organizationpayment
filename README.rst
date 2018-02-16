Organization Payment Provider
==========================

This is a plugin for `pretix`_. 
It adds a payment provider for organizations. A user can choose from a predefined list of organizations and also has to provide a member ID there. You can use it for university accounts or sponsor partners.

It was originally designed for the german Berufsgenossenschaft and Unfallkasse which pay for first aid trainings employees can do.

All texts shown to the user are customizable to make this plugin work in many different situations.

Development setup
-----------------

1. Make sure that you have a working `pretix development setup`_.

2. Clone this repository, eg to ``local/pretix-organizationpayment``.

3. Activate the virtual environment you use for pretix development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------

Copyright 2018 Felix Rindt

Released under the terms of the Apache License 2.0


.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html
