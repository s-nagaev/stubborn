# Generated by Django 3.2.11 on 2022-02-06 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0008_requestlog_status_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourcestub',
            name='Proxy to',
        ),
        migrations.AddField(
            model_name='resourcestub',
            name='proxy_destination_address',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Proxy to'),
        ),
    ]
