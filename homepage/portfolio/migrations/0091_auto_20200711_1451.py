# Generated by Django 3.0.7 on 2020-07-11 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0090_contactresponsecommon_action_arg'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='date_created',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='message',
            name='date_sent',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]