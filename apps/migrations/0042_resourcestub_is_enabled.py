# Generated by Django 3.2.18 on 2023-03-08 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0041_alter_requeststub_application'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcestub',
            name='is_enabled',
            field=models.BooleanField(default=True, verbose_name='Enabled'),
        ),
    ]