# Generated by Django 3.0.7 on 2020-07-12 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0099_auto_20200711_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
