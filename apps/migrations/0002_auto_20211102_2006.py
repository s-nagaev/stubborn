# Generated by Django 3.2.6 on 2021-11-02 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourcestub',
            name='timeout',
        ),
        migrations.AddField(
            model_name='responsestub',
            name='timeout',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Response Timeout'),
        ),
    ]
