# Generated by Django 4.1.3 on 2022-12-11 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0034_alter_category_options_alter_comment_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdetails",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="images/"),
        ),
    ]
