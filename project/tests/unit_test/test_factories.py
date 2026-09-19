from tests.factories import create_user


def test_user_factory_builds_an_unsaved_user():
    user = create_user()

    assert user.pk is None
    assert user.check_password("test-password")
