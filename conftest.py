import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


pytest_plugins = [
    "tests.unit_test.fixtures.profile",
    "tests.unit_test.fixtures.onboarding",
    "tests.unit_test.fixtures.client",
    "tests.unit_test.fixtures.attachments",
]
