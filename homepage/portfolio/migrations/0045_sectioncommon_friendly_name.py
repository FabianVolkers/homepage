# Generated by Django 3.0.7 on 2020-07-05 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0044_auto_20200705_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectioncommon',
            name='friendly_name',
            field=models.CharField(default='welcome_section', max_length=64),
            preserve_default=False,
        ),
    ]