# Generated by Django 3.0.7 on 2020-07-01 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0012_message_contact'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='uuid',
            new_name='id',
        ),
    ]
