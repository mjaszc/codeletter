# Generated by Django 4.0 on 2023-01-16 18:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_remove_comment_reply_comment_is_parent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='is_parent',
            new_name='parent',
        ),
    ]