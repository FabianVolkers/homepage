# Generated by Django 3.0.7 on 2020-07-11 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0097_auto_20200711_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='icon',
            name='slug',
            field=models.SlugField(editable=False, null=True),
        ),
    ]
