# Generated by Django 3.0.7 on 2020-07-05 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0042_auto_20200705_2058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='section',
            old_name='translantions_group',
            new_name='translations_group',
        ),
        migrations.AddField(
            model_name='section',
            name='lang',
            field=models.CharField(choices=[('de', 'German'), ('en', 'English'), ('nl', 'Dutch')], default='en', max_length=5),
        ),
    ]
