# Generated by Django 3.0.7 on 2020-07-05 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0043_auto_20200705_2059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='nav_bar_link',
        ),
        migrations.RemoveField(
            model_name='section',
            name='nav_link',
        ),
        migrations.RemoveField(
            model_name='section',
            name='position',
        ),
        migrations.RemoveField(
            model_name='section',
            name='section_type',
        ),
        migrations.CreateModel(
            name='SectionCommon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, unique=True)),
                ('nav_bar_link', models.BooleanField(default=True)),
                ('nav_link', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.NavLink')),
                ('section_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.SectionType')),
            ],
        ),
        migrations.AddField(
            model_name='section',
            name='common',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio.SectionCommon'),
        ),
    ]
