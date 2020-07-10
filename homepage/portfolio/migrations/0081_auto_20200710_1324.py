# Generated by Django 3.0.7 on 2020-07-10 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0080_auto_20200709_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionitemcommon',
            name='detail_view',
            field=models.CharField(choices=[('portfolio:detail', 'Detail View'), ('portfolio:collection', 'Collection View'), ('portfolio:page', 'Page View')], default='portfolio.views.BaseEntryView', max_length=64),
        ),
        migrations.AlterField(
            model_name='footerlink',
            name='view',
            field=models.CharField(choices=[('portfolio:detail', 'Detail View'), ('portfolio:collection', 'Collection View'), ('portfolio:page', 'Page View')], default='portfolio:project-detail', max_length=64),
        ),
        migrations.AlterField(
            model_name='navlink',
            name='view',
            field=models.CharField(choices=[('portfolio:detail', 'Detail View'), ('portfolio:collection', 'Collection View'), ('portfolio:page', 'Page View')], default='portfolio:project-detail', max_length=64),
        ),
        migrations.AlterField(
            model_name='sociallink',
            name='view',
            field=models.CharField(choices=[('portfolio:detail', 'Detail View'), ('portfolio:collection', 'Collection View'), ('portfolio:page', 'Page View')], default='portfolio:project-detail', max_length=64),
        ),
    ]