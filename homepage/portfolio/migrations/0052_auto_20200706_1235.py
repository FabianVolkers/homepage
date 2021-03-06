# Generated by Django 3.0.7 on 2020-07-06 12:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0051_auto_20200706_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseentry',
            name='translations_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portfolio_baseentry_translations', to='portfolio.TranslationsGroup'),
        ),
        migrations.AlterField(
            model_name='exhibitionpiece',
            name='translations_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portfolio_exhibitionpiece_translations', to='portfolio.TranslationsGroup'),
        ),
        migrations.AlterField(
            model_name='section',
            name='translations_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portfolio_section_translations', to='portfolio.TranslationsGroup'),
        ),
    ]
