# Generated by Django 3.0.7 on 2020-06-30 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_auto_20200630_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='spotlight',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
