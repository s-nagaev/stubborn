# Generated by Django 3.2.16 on 2022-12-26 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0026_auto_20221226_2242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestlog',
            name='application',
        ),
        migrations.RemoveField(
            model_name='requestlog',
            name='resource',
        ),
        migrations.RemoveField(
            model_name='requestlog',
            name='response',
        ),
        migrations.RemoveField(
            model_name='requeststub',
            name='application',
        ),
        migrations.RemoveField(
            model_name='resourcehook',
            name='request',
        ),
        migrations.RemoveField(
            model_name='resourcehook',
            name='resource',
        ),
        migrations.RemoveField(
            model_name='resourcestub',
            name='application',
        ),
        migrations.RemoveField(
            model_name='resourcestub',
            name='response',
        ),
        migrations.RemoveField(
            model_name='responsestub',
            name='application',
        ),
    ]
