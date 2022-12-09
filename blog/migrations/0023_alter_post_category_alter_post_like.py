# Generated by Django 4.1.3 on 2022-12-01 18:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("blog", "0022_alter_post_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="blog.category",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="like",
            field=models.ManyToManyField(
                blank=True, related_name="like", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]