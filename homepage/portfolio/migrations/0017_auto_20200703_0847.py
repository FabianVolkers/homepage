# Generated by Django 3.0.7 on 2020-07-03 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0016_section_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectiontype',
            name='default_position',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='section',
            name='position',
            field=models.IntegerField(null=True),
        ),
    ]
