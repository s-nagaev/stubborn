# Generated by Django 3.2.11 on 2022-02-06 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_resourcestub_proxy to'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestlog',
            name='status_code',
            field=models.IntegerField(blank=True, null=True, verbose_name='Status Code'),
        ),
    ]
