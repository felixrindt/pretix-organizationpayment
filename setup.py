import os
from distutils.command.build import build

from django.core import management
from setuptools import setup, find_packages


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


class CustomBuild(build):
    def run(self):
        management.call_command('compilemessages', verbosity=1, interactive=False)
        build.run(self)


cmdclass = {
    'build': CustomBuild
}


setup(
    name='pretix-organizationpayment',
    version='2.0.0',
    description='This pretix plugin adds a flexible payment provider. A user can select one of the configured Organizations and also provides data in an additional field with configurable annotation.',
    long_description=long_description,
    url='https://github.com/felixrindt/pretix-organizationpayment',
    author='Felix Rindt',
    author_email='felix@rindt.me',
    license='Apache Software License',

    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_organizationpayment=pretix_organizationpayment:PretixPluginMeta
""",
)
