from django.db import migrations, models
from django.utils.text import slugify


def populate_unique_names(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    pending_names = {}
    names_by_author = {}

    posts = Post.objects.order_by("author_id", "pk").only(
        "pk", "author_id", "title"
    )
    for post in posts:
        unique_name = slugify(post.title)
        if not unique_name:
            raise RuntimeError(
                f"Cannot generate a unique name for post ID {post.pk}: "
                "its title produces an empty slug."
            )

        key = (post.author_id, unique_name)
        previous = names_by_author.get(key)
        if previous is not None:
            raise RuntimeError(
                "Cannot migrate duplicate post unique names for author ID "
                f"{post.author_id}: posts {previous[0]} ({previous[1]!r}) and "
                f"{post.pk} ({post.title!r}) both produce '{unique_name}'."
            )

        names_by_author[key] = (post.pk, post.title)
        pending_names[post.pk] = unique_name

    for post_id, unique_name in pending_names.items():
        Post.objects.filter(pk=post_id).update(unique_name=unique_name)


def clear_unique_names(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    Post.objects.update(unique_name=None)


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0002_post_author_public_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="unique_name",
            field=models.SlugField(max_length=200, null=True),
        ),
        migrations.RunPython(populate_unique_names, clear_unique_names),
        migrations.AlterField(
            model_name="post",
            name="unique_name",
            field=models.SlugField(editable=False, max_length=200),
        ),
        migrations.AddConstraint(
            model_name="post",
            constraint=models.UniqueConstraint(
                fields=("author", "unique_name"),
                name="post_author_unique_name",
            ),
        ),
    ]
