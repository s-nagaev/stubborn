# Generated by Django 3.2.13 on 2022-06-03 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0019_auto_20220603_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcestub',
            name='tail',
            field=models.CharField(default='', max_length=120, verbose_name='URL Tail'),
        ),
        migrations.AlterField(
            model_name='resourcestub',
            name='slug',
            field=models.SlugField(allow_unicode=True, verbose_name='Slug'),
        ),
    ]
