# Generated by Django 4.1.3 on 2022-11-28 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0017_category_post_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=50),
        ),
    ]
