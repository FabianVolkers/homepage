# Generated by Django 3.0.7 on 2020-07-12 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0101_remove_pagecommon_template_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sectiontype',
            name='template_name',
        ),
    ]
