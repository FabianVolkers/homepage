# Generated by Django 3.0.7 on 2020-07-06 20:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0068_exhibitionpiececommon_friendly_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baseentry',
            name='created',
        ),
        migrations.RemoveField(
            model_name='baseentry',
            name='detail_view',
        ),
        migrations.RemoveField(
            model_name='baseentry',
            name='image',
        ),
        migrations.RemoveField(
            model_name='baseentry',
            name='parent_section',
        ),
        migrations.RemoveField(
            model_name='baseentry',
            name='spotlight',
        ),
    ]