# Generated by Django 3.0.7 on 2020-07-10 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0082_auto_20200710_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionitemcommon',
            name='detail_view',
            field=models.CharField(choices=[('portfolio:detail', 'Detail View'), ('portfolio:collection', 'Collection View'), ('portfolio:page', 'Page View')], default='portfolio:detail', max_length=64),
        ),
    ]