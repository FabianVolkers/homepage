# Generated by Django 3.0.7 on 2020-07-01 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0009_auto_20200630_1847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='url',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='url',
        ),
        migrations.RemoveField(
            model_name='project',
            name='url',
        ),
        migrations.AddField(
            model_name='collection',
            name='slug',
            field=models.SlugField(default='test-slug', editable=False, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='slug',
            field=models.SlugField(default='test-slug', editable=False, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='slug',
            field=models.SlugField(default='test-slug', editable=False, max_length=100),
            preserve_default=False,
        ),
    ]
