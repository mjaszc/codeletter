# Generated by Django 4.1.4 on 2023-01-05 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_remove_notification_post_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="post_slug",
            field=models.SlugField(auto_created=True, blank=True, max_length=255),
        ),
    ]