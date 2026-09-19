import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from drf_spectacular.generators import SchemaGenerator


def test_rest_framework_is_installed():
    assert 'rest_framework' in settings.INSTALLED_APPS


def test_rest_framework_authentication_default():
    assert settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] == [
        'rest_framework.authentication.SessionAuthentication',
    ]


def test_rest_framework_permission_default():
    assert settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] == [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]


def test_rest_framework_pagination_default():
    assert settings.REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] == (
        'rest_framework.pagination.PageNumberPagination'
    )
    assert settings.REST_FRAMEWORK['PAGE_SIZE'] == 20


def test_rest_framework_renderer_defaults():
    assert settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] == [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]


def test_environment_defaults_to_development():
    assert settings.ENVIRONMENT == 'development'


def test_openapi_schema_documents_public_author_routes():
    schema = SchemaGenerator().get_schema(request=None, public=True)

    assert "/api/authors/{public_username}/" in schema["paths"]
    assert "/api/authors/{public_username}/posts/" in schema["paths"]
    assert "/api/authors/{public_username}/posts/{unique_name}/" in schema["paths"]
    assert schema["servers"] == [
        {
            "url": "http://localhost:8000",
            "description": "Current environment",
        }
    ]


def test_production_openapi_schema_excludes_public_routes():
    project_root = Path(__file__).parents[4]
    environment = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "app.settings",
        "ENVIRONMENT": "production",
        "PYTHONPATH": str(project_root / "project"),
    }
    command = (
        "import django; django.setup(); "
        "from drf_spectacular.generators import SchemaGenerator; "
        "print(sorted(SchemaGenerator().get_schema(request=None, public=True)['paths']))"
    )

    result = subprocess.run(
        [sys.executable, "-c", command],
        cwd=project_root,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "[]"
