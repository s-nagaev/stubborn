# Generated by Django 3.2.16 on 2022-12-26 22:46

from django.db import migrations


def remove_resourcehook_constraint(apps, schema_editor):
    try:
        migrations.RemoveConstraint(
            model_name='resourcehook',
            name='unique_order_per_resource',
        ),
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0027_auto_20221226_2244'),
    ]

    operations = [
        migrations.RunPython(remove_resourcehook_constraint)
    ]
