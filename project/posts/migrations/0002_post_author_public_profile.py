from django.conf import settings
from django.db import migrations, models


def migrate_authors_to_profiles(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    PublicProfile = apps.get_model("profiles", "PublicProfile")
    profile_ids_by_user = dict(PublicProfile.objects.values_list("user_id", "pk"))
    author_ids = set(Post.objects.values_list("user_author_id", flat=True))
    missing_author_ids = sorted(author_ids - profile_ids_by_user.keys())

    if missing_author_ids:
        raise RuntimeError(
            "Cannot migrate post authors without public profiles for user IDs: "
            f"{missing_author_ids}."
        )

    for user_id, profile_id in profile_ids_by_user.items():
        Post.objects.filter(user_author_id=user_id).update(profile_author_id=profile_id)


def migrate_authors_to_users(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    PublicProfile = apps.get_model("profiles", "PublicProfile")
    user_ids_by_profile = dict(PublicProfile.objects.values_list("pk", "user_id"))
    profile_ids = set(Post.objects.values_list("profile_author_id", flat=True))
    missing_profile_ids = sorted(profile_ids - user_ids_by_profile.keys())

    if missing_profile_ids:
        raise RuntimeError(
            "Cannot reverse post author migration without users for public profile "
            f"IDs: {missing_profile_ids}."
        )

    for profile_id, user_id in user_ids_by_profile.items():
        Post.objects.filter(profile_author_id=profile_id).update(user_author_id=user_id)


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("posts", "0001_initial"),
        ("profiles", "0003_publicprofile"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="author",
            new_name="user_author",
        ),
        migrations.AlterField(
            model_name="post",
            name="user_author",
            field=models.ForeignKey(
                null=True,
                on_delete=models.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="profile_author",
            field=models.ForeignKey(
                null=True,
                on_delete=models.CASCADE,
                related_name="+",
                to="profiles.publicprofile",
            ),
        ),
        migrations.RunPython(migrate_authors_to_profiles, migrate_authors_to_users),
        migrations.RemoveField(
            model_name="post",
            name="user_author",
        ),
        migrations.RenameField(
            model_name="post",
            old_name="profile_author",
            new_name="author",
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name="posts",
                to="profiles.publicprofile",
            ),
        ),
    ]
