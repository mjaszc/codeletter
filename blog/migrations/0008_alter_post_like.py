# Generated by Django 4.1.3 on 2022-11-16 20:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("blog", "0007_alter_like_post_alter_like_user_alter_post_like"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="like",
            field=models.ManyToManyField(
                default=0, related_name="like", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]