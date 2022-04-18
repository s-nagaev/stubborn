# Generated by Django 3.2.11 on 2022-03-26 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0009_auto_20220206_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestlog',
            name='destination_url',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Destination URL'),
        ),
        migrations.AddField(
            model_name='requestlog',
            name='proxied',
            field=models.BooleanField(default=False, verbose_name='Proxied'),
        ),
    ]