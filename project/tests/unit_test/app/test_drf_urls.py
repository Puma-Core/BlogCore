import importlib
from contextlib import contextmanager

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import Resolver404, clear_url_caches, resolve

from app import router as app_router
from app import urls


@contextmanager
def api_environment(environment: str):
    with override_settings(ENVIRONMENT=environment):
        importlib.reload(app_router)
        importlib.reload(urls)
        clear_url_caches()
        yield

    importlib.reload(app_router)
    importlib.reload(urls)
    clear_url_caches()


def test_api_root_is_not_exposed():
    with api_environment('development'):
        assert settings.ENVIRONMENT == 'development'
        with pytest.raises(Resolver404):
            resolve('/api/')


def test_api_auth_urls_resolves_in_development():
    with api_environment('development'):
        resolved = resolve('/api/auth/login/')
        assert resolved.url_name == 'login'


def test_openapi_schema_resolves_in_development():
    with api_environment('development'):
        resolved = resolve('/api/schema/')
        assert resolved.url_name == 'schema'


def test_local_attachment_media_resolves_without_debug_mode():
    with override_settings(DEBUG=False):
        with api_environment('development'):
            resolved = resolve('/media/attachments/photo.webp')

    assert resolved.kwargs == {
        'path': 'attachments/photo.webp',
        'document_root': settings.MEDIA_ROOT,
    }


@pytest.mark.parametrize(
    "path",
    [
        "/api/authors/test-user.json",
        "/api/authors/test-user/posts.json",
    ],
)
def test_api_routes_accept_format_suffixes_in_development(path: str):
    with api_environment('development'):
        assert resolve(path).url_name in {'author-detail', 'author-post-list'}


def test_public_api_route_resolves_in_production():
    with api_environment('production'):
        resolved = resolve('/api/authors/test-user/')
        assert resolved.url_name == 'author-detail'
        resolved = resolve('/api/authors/test-user/posts/')
        assert resolved.url_name == 'author-post-list'
        resolved = resolve('/api/authors/test-user/posts/test-post/')
        assert resolved.url_name == 'author-post-detail'

        with pytest.raises(Resolver404):
            resolve('/api/auth/login/')
        with pytest.raises(Resolver404):
            resolve('/api/schema/')
        with pytest.raises(Resolver404):
            resolve('/api/authors/test-user.json')
        with pytest.raises(Resolver404):
            resolve('/media/attachments/photo.webp')
