# Generated by Django 3.0.7 on 2020-07-03 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0032_auto_20200703_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='navlink',
            name='position',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], unique=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='position',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, unique=True),
        ),
    ]
