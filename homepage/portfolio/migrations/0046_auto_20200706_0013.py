# Generated by Django 3.0.7 on 2020-07-06 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0045_sectioncommon_friendly_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='common',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='portfolio.SectionCommon'),
        ),
    ]
