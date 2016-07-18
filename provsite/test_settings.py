"""
Django settings for testing provsite project; needed when using additional 
unmanaged databases/tables (with "managed = False" in their Meta class)

Use these settings for testing, together with --nomigrations 
(for suppressing migrations; otherwise it won't work!),
e.g.: 
python manage.py test --settings=provsite.test_settings --nomigrations
"""

import os
import sys

from provsite.settings import *
from django.test.runner import DiscoverRunner
from django.apps import apps

# see http://blog.birdhouse.org/2015/03/25/django-unit-tests-against-unmanaged-databases/
# and the Caktus group: https://www.caktusgroup.com/blog/2010/09/24/simplifying-the-testing-of-unmanaged-database-models-in-django/
# (or http://bit.ly/1N8TcHW)
class UnManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in the Django
    project managed for the duration of the test run.
    """

    def setup_test_environment(self, *args, **kwargs):
        self.unmanaged_models = [m for m in apps.get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True
        super(UnManagedModelTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(UnManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False

# Set Django's test runner to the custom class defined above
TEST_RUNNER = 'provsite.test_settings.UnManagedModelTestRunner'