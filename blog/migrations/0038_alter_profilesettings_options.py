# Generated by Django 4.1.3 on 2022-12-11 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0037_rename_userdetails_profilesettings"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="profilesettings",
            options={
                "verbose_name": "Profile Setting",
                "verbose_name_plural": "Profile Settings",
            },
        ),
    ]
